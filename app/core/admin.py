from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from wtforms import TextAreaField, PasswordField, SelectField, StringField, DateTimeField
from wtforms.validators import Optional
from markupsafe import Markup
import re
from datetime import datetime

from app.core.config import settings 
from app.core.security import verify_password, get_password_hash
from app.db.session import SessionLocal

from app.models.product import Product, ProductFeature, ProductWhyUs, ProductFAQ
from app.models.solutions import Solution, SolutionFeature, SolutionWhyUs, SolutionRelatedProduct, SolutionFAQ
from app.models.blog import Article, Author, Category, User

def format_relation_link(model, attribute):
    related_obj = getattr(model, attribute)
    if not related_obj:
        return ""
    name = str(related_obj)
    return Markup(f'<a href="?search={name}" style="text-decoration: underline; color: #3b82f6;">{name}</a>')

class LineSeparatedListField(TextAreaField):
    def _value(self):
        if self.data and isinstance(self.data, list):
            return "\n".join(self.data)
        return ""

    def process_formdata(self, valuelist):
        if valuelist and valuelist[0]:
            self.data = [x.strip() for x in valuelist[0].split('\n') if x.strip()]
        else:
            self.data = []

class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        db = SessionLocal()
        try:
            user = db.query(User).filter(User.username == username).first()
            if user and verify_password(password, user.password_hash):
                if not user.is_active:
                    return False
                request.session.update({
                    "token": "authenticated",
                    "user_id": str(user.id),
                    "role": user.role,
                    "username": user.username
                })
                return True
        finally:
            db.close()
            
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return bool(request.session.get("token"))

authentication_backend = AdminAuth(secret_key=settings.SECRET_KEY)

class UserAdmin(ModelView, model=User):
    category = "System"
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-users"

    column_list = [User.username, User.role, User.is_active]
    form_excluded_columns = [User.password_hash]

    form_extra_fields = {
        "password": PasswordField("New Password"),
        "role": SelectField(
            "Role",
            choices=[("admin", "Admin"), ("editor", "Editor")],
            default="editor"
        )
    }

    def is_accessible(self, request: Request) -> bool:
        return request.session.get("role") == "admin"

    def is_visible(self, request: Request) -> bool:
        return request.session.get("role") == "admin"

    async def on_model_change(self, data, model, is_created, request):
        plain_password = data.get("password")
        
        if plain_password:
            data["password_hash"] = get_password_hash(plain_password)
            del data["password"]
        elif is_created:
             raise Exception("Password is required for new users.")
        else:
            if "password" in data:
                del data["password"]

class ArticleAdmin(ModelView, model=Article):
    category = "Blog Manager"
    name = "Article"
    name_plural = "Articles"
    icon = "fa-solid fa-newspaper"
    
    column_list = [Article.title, Article.publisher, Article.published_at]
    column_searchable_list = [Article.title, Article.slug, Article.content, Article.summary]
    column_sortable_list = [Article.published_at, Article.title]
    form_excluded_columns = [Article.created_at, Article.updated_at, Article.id]

    form_ajax_refs = {
        "publisher": { "fields": ["name"], "order_by": "name", "placeholder": "Select Author..." },
        "categories": { "fields": ["name"], "order_by": "name", "placeholder": "Add Categories..." }
    }
    
    form_overrides = dict(content=TextAreaField, summary=TextAreaField)
    
    form_extra_fields = {
        "slug": StringField("URL Slug (Auto-generated if empty)", validators=[Optional()]),
        "published_at": DateTimeField("Published Date (Leave empty for Now)", validators=[Optional()], format="%Y-%m-%d %H:%M:%S")
    }

    form_args = {
        "content": dict(label="Main Content", render_kw={"rows": 20, "style": "width: 100%; font-family: monospace;"}), 
        "summary": dict(label="Short Summary", render_kw={"rows": 4, "style": "width: 100%;"})
    }
    
    column_labels = {
        Article.image_url: "Cover Image URL"
    }

    def get_query(self, request: Request):
        query = super().get_query(request)
        role = request.session.get("role")
        user_id = request.session.get("user_id")

        if role != "admin" and user_id:
            query = query.join(Article.publisher).join(Author.user).filter(User.id == user_id)
        
        return query

    async def on_model_change(self, data, model, is_created, request):
        if not data.get("slug") and data.get("title"):
            slug = data["title"].lower().strip()
            slug = re.sub(r'[^\w\s-]', '', slug)
            slug = re.sub(r'[\s_-]+', '-', slug)
            data["slug"] = slug

        if not data.get("published_at"):
            data["published_at"] = datetime.now()

        role = request.session.get("role")
        user_id = request.session.get("user_id")

        if role != "admin" and is_created:
            db = SessionLocal()
            try:
                author = db.query(Author).filter(Author.user_id == user_id).first()
                if author:
                    data["publisher_id"] = author.id
                else:
                    raise Exception("You must have an Author Profile linked to your User to post.")
            finally:
                db.close()

class AuthorAdmin(ModelView, model=Author):
    category = "Blog Manager"
    name = "Author"
    name_plural = "Authors"
    icon = "fa-solid fa-user-pen"
    column_list = [Author.name, Author.user]
    column_searchable_list = [Author.name]
    form_excluded_columns = [Author.created_at, Author.updated_at]
    
    form_ajax_refs = {
        "user": { "fields": ["username"], "order_by": "username", "placeholder": "Link to Login User..." }
    }

class CategoryAdmin(ModelView, model=Category):
    category = "Blog Manager"
    name = "Category"
    name_plural = "Categories"
    icon = "fa-solid fa-tag"
    column_list = [Category.name]
    column_searchable_list = [Category.name]
    form_excluded_columns = [Category.created_at, Category.updated_at]

class ProductAdmin(ModelView, model=Product):
    category = "Product Manager"
    name = "Product Page"
    name_plural = "Products"
    icon = "fa-solid fa-box-open"
    column_list = [Product.name, Product.slug, Product.category, Product.updated_at]
    column_searchable_list = [Product.name, Product.slug, Product.hero_title]
    form_excluded_columns = [Product.id, Product.created_at, Product.updated_at, Product.features, Product.why_us, Product.faqs]
    form_overrides = dict(hero_subtitle=TextAreaField)
    form_args = { "hero_subtitle": dict(render_kw={"rows": 4, "style": "width: 100%;"}) }
    column_labels = { Product.hero_title: "Hero Banner Title", Product.hero_subtitle: "Hero Banner Text" }

class ProductFeatureAdmin(ModelView, model=ProductFeature):
    category = "Product Manager"
    name = "Product Feature"
    name_plural = "Features"
    icon = "fa-solid fa-list-check"

    column_list = [ProductFeature.product, ProductFeature.tab_label, ProductFeature.sequence]
    column_sortable_list = [ProductFeature.product_id, ProductFeature.sequence]
    column_searchable_list = ["product.name", ProductFeature.tab_label, ProductFeature.content_title, ProductFeature.content_description]
    column_formatters = { ProductFeature.product: format_relation_link }

    form_excluded_columns = [ProductFeature.id, ProductFeature.created_at, ProductFeature.updated_at]
    form_ajax_refs = { "product": { "fields": ["name"], "order_by": "name", "placeholder": "Search for a Product..." } }
    
    form_overrides = dict(content_description=TextAreaField, benefits=LineSeparatedListField)
    form_args = {
        "content_description": dict(render_kw={"rows": 10, "style": "width: 100%;"}),
        "benefits": dict(label="Benefits List", description="Type one benefit per line.", render_kw={"rows": 8, "style": "width: 100%;", "placeholder": "Fast Processing\nSecure Data"})
    }

class ProductWhyUsAdmin(ModelView, model=ProductWhyUs):
    category = "Product Manager"
    name = "Why Us Item"
    name_plural = "Why Us Section"
    icon = "fa-solid fa-thumbs-up"

    column_list = [ProductWhyUs.product, ProductWhyUs.card_label, ProductWhyUs.sequence]
    column_searchable_list = ["product.name", ProductWhyUs.card_label, ProductWhyUs.section_title]
    column_formatters = { ProductWhyUs.product: format_relation_link }

    form_excluded_columns = [ProductWhyUs.id, ProductWhyUs.created_at, ProductWhyUs.updated_at]
    form_ajax_refs = { "product": { "fields": ["name"], "order_by": "name", "placeholder": "Search for a Product..." } }

class ProductFAQAdmin(ModelView, model=ProductFAQ):
    category = "Product Manager"
    name = "Product FAQ"
    name_plural = "FAQs"
    icon = "fa-solid fa-circle-question"

    column_list = [ProductFAQ.product, ProductFAQ.question, ProductFAQ.sequence]
    column_searchable_list = ["product.name", ProductFAQ.question, ProductFAQ.answer]
    column_formatters = { ProductFAQ.product: format_relation_link }
    
    form_excluded_columns = [ProductFAQ.id, ProductFAQ.created_at, ProductFAQ.updated_at]
    form_ajax_refs = { "product": { "fields": ["name"], "order_by": "name", "placeholder": "Search for a Product..." } }
    form_overrides = dict(answer=TextAreaField)
    form_args = { "answer": dict(render_kw={"rows": 6, "style": "width: 100%;"}) }

class SolutionAdmin(ModelView, model=Solution):
    category = "Solution Manager"
    name = "Solution Page"
    name_plural = "Solutions"
    icon = "fa-solid fa-puzzle-piece"
    column_list = [Solution.name, Solution.category, Solution.slug]
    column_searchable_list = [Solution.name, Solution.hero_title]
    
    form_excluded_columns = [
        Solution.id, Solution.created_at, Solution.updated_at, 
        Solution.features, Solution.why_us, Solution.faqs, Solution.related_products
    ]
    
    form_overrides = dict(hero_subtitle=TextAreaField)
    form_args = { "hero_subtitle": dict(render_kw={"rows": 4, "style": "width: 100%;"}) }
    column_labels = { Solution.hero_title: "Hero Banner Title", Solution.hero_subtitle: "Hero Banner Text" }

class SolutionFeatureAdmin(ModelView, model=SolutionFeature):
    category = "Solution Manager"
    name = "Solution Feature"
    name_plural = "Features"
    icon = "fa-solid fa-list-check"

    column_list = [SolutionFeature.solution, SolutionFeature.tab_label, SolutionFeature.sequence]
    column_searchable_list = ["solution.name", SolutionFeature.tab_label, SolutionFeature.content_title]
    column_formatters = { SolutionFeature.solution: format_relation_link }

    form_excluded_columns = [SolutionFeature.id, SolutionFeature.created_at, SolutionFeature.updated_at]
    form_ajax_refs = { "solution": { "fields": ["name"], "order_by": "name", "placeholder": "Search for a Solution..." } }
    form_overrides = dict(content_description=TextAreaField, benefits=LineSeparatedListField)
    form_args = {
        "content_description": dict(render_kw={"rows": 10, "style": "width: 100%;"}),
        "benefits": dict(label="Benefits List", description="Type one benefit per line.", render_kw={"rows": 8, "style": "width: 100%;", "placeholder": "Benefit A\nBenefit B"})
    }

class SolutionWhyUsAdmin(ModelView, model=SolutionWhyUs):
    category = "Solution Manager"
    name = "Why Us Item"
    name_plural = "Why Us Section"
    icon = "fa-solid fa-thumbs-up"

    column_list = [SolutionWhyUs.solution, SolutionWhyUs.title, SolutionWhyUs.sequence]
    column_searchable_list = ["solution.name", SolutionWhyUs.title, SolutionWhyUs.description]
    column_formatters = { SolutionWhyUs.solution: format_relation_link }
    
    form_excluded_columns = [SolutionWhyUs.id, SolutionWhyUs.created_at, SolutionWhyUs.updated_at]
    form_ajax_refs = { "solution": { "fields": ["name"], "order_by": "name", "placeholder": "Select Solution..." } }
    form_overrides = dict(description=TextAreaField)
    form_args = { "description": dict(render_kw={"rows": 6, "style": "width: 100%;"}) }

class SolutionRelatedProductAdmin(ModelView, model=SolutionRelatedProduct):
    category = "Solution Manager"
    name = "Related Product"
    name_plural = "Related Products"
    icon = "fa-solid fa-link"

    column_list = [SolutionRelatedProduct.solution, SolutionRelatedProduct.product, SolutionRelatedProduct.sequence]
    column_searchable_list = ["solution.name", "product.name"]
    column_formatters = { 
        SolutionRelatedProduct.solution: format_relation_link,
        SolutionRelatedProduct.product: format_relation_link 
    }

    form_excluded_columns = [SolutionRelatedProduct.id, SolutionRelatedProduct.created_at, SolutionRelatedProduct.updated_at]
    form_ajax_refs = {
        "solution": { "fields": ["name"], "order_by": "name", "placeholder": "Which Solution Page?" },
        "product": { "fields": ["name"], "order_by": "name", "placeholder": "Link to which Product?" }
    }

class SolutionFAQAdmin(ModelView, model=SolutionFAQ):
    category = "Solution Manager"
    name = "Solution FAQ"
    name_plural = "FAQs"
    icon = "fa-solid fa-circle-question"

    column_list = [SolutionFAQ.solution, SolutionFAQ.question, SolutionFAQ.sequence]
    column_searchable_list = ["solution.name", SolutionFAQ.question, SolutionFAQ.answer]
    column_formatters = { SolutionFAQ.solution: format_relation_link }
    
    form_excluded_columns = [SolutionFAQ.id, SolutionFAQ.created_at, SolutionFAQ.updated_at]
    form_ajax_refs = { "solution": { "fields": ["name"], "order_by": "name", "placeholder": "Select Solution..." } }
    form_overrides = dict(answer=TextAreaField)
    form_args = { "answer": dict(render_kw={"rows": 6, "style": "width: 100%;"}) }

def setup_admin(app, engine):
    admin = Admin(
        app, 
        engine, 
        authentication_backend=authentication_backend,
        title="Content Management System",
        templates_dir="templates"
    )

    admin.add_view(UserAdmin)
    admin.add_view(ArticleAdmin)
    admin.add_view(AuthorAdmin)
    admin.add_view(CategoryAdmin)

    admin.add_view(ProductAdmin)
    admin.add_view(ProductFeatureAdmin)
    admin.add_view(ProductWhyUsAdmin)
    admin.add_view(ProductFAQAdmin)

    admin.add_view(SolutionAdmin)
    admin.add_view(SolutionFeatureAdmin)
    admin.add_view(SolutionWhyUsAdmin)
    admin.add_view(SolutionRelatedProductAdmin)
    admin.add_view(SolutionFAQAdmin)

    return admin