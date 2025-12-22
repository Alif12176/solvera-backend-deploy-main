from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from wtforms import TextAreaField, PasswordField, SelectField, StringField, DateTimeField, HiddenField
from wtforms.widgets import TextArea
from wtforms.validators import Optional, DataRequired, ValidationError
from markupsafe import Markup
import re
import uuid
import html
from datetime import datetime

from app.core.config import settings 
from app.core.security import verify_password, get_password_hash
from app.db.session import SessionLocal

from app.models.product import Product, ProductFeature, ProductWhyUs, ProductFAQ, ProductSocialTrustLink
from app.models.solutions import Solution, SolutionFeature, SolutionWhyUs, SolutionRelatedProduct, SolutionFAQ, SolutionSocialTrustLink
from app.models.blog import Article, Author, Category, User
from app.models.social_trust import SocialTrust
from app.models.service import ServicePage, ServiceFocusItem, ServiceQuickStep, ServiceOffering, ServiceMethodology, ServiceCompetency

def unique_article_title_validator(form, field):
    if field.object_data == field.data:
        return

    db = SessionLocal()
    try:
        existing = db.query(Article).filter(Article.title == field.data).first()
        
        if existing:
            if hasattr(form, 'publisher') and form.publisher.data:
                if isinstance(form.publisher.data, str) and form.publisher.data.isdigit():
                    author_obj = db.query(Author).get(int(form.publisher.data))
                    if author_obj:
                        form.publisher.data = author_obj

            if hasattr(form, 'categories') and form.categories.data:
                new_data = []
                for item in form.categories.data:
                    if isinstance(item, str) and item.isdigit():
                        cat_obj = db.query(Category).get(int(item))
                        if cat_obj:
                            new_data.append(cat_obj)
                    else:
                        new_data.append(item)
                form.categories.data = new_data

            raise ValidationError(f"An article with the title '{field.data}' already exists.")
    finally:
        db.close()

class QuillEditorWidget(TextArea):
    def __call__(self, field, **kwargs):
        kwargs['style'] = 'display:none;'
        if 'class_' not in kwargs:
            kwargs['class_'] = ''
        
        textarea_html = super().__call__(field, **kwargs)
        
        editor_id = f"quill_editor_{field.id}"
        
        quill_html = f"""
        <div style="background: white; margin-bottom: 20px;">
            <link href="https://cdn.quilljs.com/1.3.6/quill.snow.css" rel="stylesheet">
            <div id="{editor_id}" style="height: 300px; color: black;">
                {field.data or ''}
            </div>
        </div>
        
        <script src="https://cdn.quilljs.com/1.3.6/quill.js"></script>
        <script>
            (function() {{
                var quill = new Quill('#{editor_id}', {{
                    theme: 'snow',
                    modules: {{
                        toolbar: [
                            [{{ 'header': [1, 2, 3, false] }}],
                            ['bold', 'italic', 'underline', 'strike'],
                            ['blockquote', 'code-block'],
                            [{{ 'list': 'ordered'}}, {{ 'list': 'bullet' }}],
                            [{{ 'indent': '-1'}}, {{ 'indent': '+1' }}],
                            ['link', 'image'],
                            ['clean']
                        ]
                    }}
                }});
                
                var textarea = document.getElementById('{field.id}');
                
                quill.on('text-change', function() {{
                    textarea.value = quill.root.innerHTML;
                }});
            }})();
        </script>
        """
        
        return Markup(str(textarea_html) + quill_html)

class RichTextField(TextAreaField):
    widget = QuillEditorWidget()

def format_relation_link(model, attribute):
    related_obj = getattr(model, attribute)
    if not related_obj:
        return ""
    name = str(related_obj)
    return Markup(f'<a href="?search={name}" style="text-decoration: underline; color: #3b82f6;">{name}</a>')

def format_image_preview(model, attribute):
    url = getattr(model, attribute)
    if not url:
        return ""
    return Markup(f'<img src="{url}" height="40" style="border-radius: 4px; border: 1px solid #eee; background: white;" />')

def format_long_text(model, attribute):
    value = getattr(model, attribute)
    if not value:
        return ""
    
    safe_value = html.unescape(str(value))
    unique_id = f"modal_{uuid.uuid4().hex}"
    
    html_content = f"""
    <div style="
        max-height: 120px; 
        max-width: 600px; 
        overflow: hidden; 
        position: relative; 
        margin-bottom: 8px; 
        border: 1px solid #e5e7eb; 
        padding: 12px; 
        border-radius: 6px; 
        background: #ffffff;
        white-space: normal !important;
        word-wrap: break-word;
    ">
        <div style="opacity: 0.9; font-size: 0.95em; color: #4b5563; line-height: 1.5;">
            {safe_value}
        </div>
        <div style="position: absolute; bottom: 0; left: 0; width: 100%; height: 50px; background: linear-gradient(to bottom, transparent, #ffffff);"></div>
    </div>
    
    <button type="button" 
            onclick="document.getElementById('{unique_id}').style.display='flex'" 
            style="background: #eff6ff; border: 1px solid #bfdbfe; color: #1d4ed8; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 0.85rem; font-weight: 500; display: inline-flex; align-items: center; gap: 6px; transition: all 0.2s;">
        <i class="fa-solid fa-expand"></i> Show Full Content
    </button>

    <div id="{unique_id}" 
         style="display: none; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.7); z-index: 9999999; justify-content: center; align-items: center; backdrop-filter: blur(4px);">
        <div style="background: white; width: 90%; max-width: 900px; height: 85%; border-radius: 12px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04); display: flex; flex-direction: column; overflow: hidden;">
            <div style="padding: 1.25rem 1.5rem; border-bottom: 1px solid #e5e7eb; display: flex; justify-content: space-between; align-items: center; background: #f9fafb;">
                <h3 style="margin: 0; font-size: 1.1rem; font-weight: 600; color: #111827;">Content Preview</h3>
                <button onclick="document.getElementById('{unique_id}').style.display='none'" 
                        style="background: transparent; border: none; font-size: 1.5rem; cursor: pointer; color: #6b7280; padding: 4px 8px; border-radius: 4px;">
                    &times;
                </button>
            </div>
            <div style="padding: 2rem; overflow-y: auto; line-height: 1.6; font-size: 1rem; color: #374151; white-space: normal !important; word-wrap: break-word;">
                {safe_value}
            </div>
        </div>
    </div>
    """
    return Markup(html_content)

def generate_unique_slug(db, model, source_text, current_id=None):
    if not source_text:
        return ""

    slug = source_text.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', '-', slug)
    
    original_slug = slug
    counter = 1
    
    while True:
        query = db.query(model).filter(model.slug == slug)
        
        if current_id:
            query = query.filter(model.id != current_id)
            
        if not query.first():
            break
            
        slug = f"{original_slug}-{counter}"
        counter += 1
        
    return slug

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
    form_excluded_columns = [User.id, User.author_profile]

    form_overrides = {
        "password_hash": PasswordField
    }
    
    form_args = {
        "password_hash": {
            "label": "Password",
            "description": "Leave empty to keep current password (if editing)."
        }
    }

    form_extra_fields = {
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
        if is_created:
            db = SessionLocal()
            try:
                existing = db.query(User).filter(User.username == data.get("username")).first()
                if existing:
                    raise ValidationError(f"Username '{data.get('username')}' is already taken.")
            finally:
                db.close()

        incoming_password = data.get("password_hash")
        if incoming_password:
            data["password_hash"] = get_password_hash(incoming_password)
        elif is_created:
             raise ValidationError("Password is required for new users.")
        else:
            if "password_hash" in data:
                del data["password_hash"]

class ArticleAdmin(ModelView, model=Article):
    category = "Blog Manager"
    name = "Article"
    name_plural = "Articles"
    icon = "fa-solid fa-newspaper"
    
    column_list = [Article.title, Article.publisher, Article.published_at]
    
    column_details_list = [
        Article.id, 
        Article.title, 
        Article.slug, 
        Article.publisher, 
        Article.categories, 
        Article.summary, 
        Article.content, 
        Article.image_url, 
        Article.published_at,
        Article.created_at,
        Article.updated_at
    ]
    
    column_searchable_list = [Article.title, Article.slug, Article.content, Article.summary]
    column_sortable_list = [Article.published_at, Article.title]
    
    form_excluded_columns = [Article.created_at, Article.updated_at]

    form_ajax_refs = {
        "publisher": { "fields": ["name"], "order_by": "name", "placeholder": "Select Author..." },
        "categories": { "fields": ["name"], "order_by": "name", "placeholder": "Add Categories..." }
    }
    
    form_overrides = dict(content=RichTextField, summary=RichTextField, id=HiddenField)
    
    form_extra_fields = {
        "published_at": DateTimeField("Published Date (Leave empty for Now)", validators=[Optional()], format="%Y-%m-%d %H:%M:%S")
    }

    form_args = {
        "summary": dict(label="Short Summary"),
        "title": dict(validators=[DataRequired(), unique_article_title_validator]),
        "slug": dict(
            label="URL Slug (Auto-generated)", 
            render_kw={"disabled": "disabled"},
            validators=[Optional()] 
        )
    }
    
    column_labels = {
        Article.image_url: "Cover Image URL"
    }
    
    column_formatters = {
        Article.image_url: format_image_preview,
        Article.summary: format_long_text,
        Article.content: format_long_text
    }
    
    column_formatters_detail = {
        Article.image_url: format_image_preview,
        Article.summary: format_long_text,
        Article.content: format_long_text
    }

    def get_query(self, request: Request):
        query = super().get_query(request)
        role = request.session.get("role")
        user_id = request.session.get("user_id")

        if role != "admin" and user_id:
            query = query.join(Article.publisher).join(Author.user).filter(User.id == user_id)
        
        return query

    async def on_model_change(self, data, model, is_created, request):
        db = SessionLocal()
        try:
            if not is_created and model.slug:
                if "slug" in data:
                    del data["slug"]
            elif data.get("title"):
                data["slug"] = generate_unique_slug(db, Article, data["title"], model.id if not is_created else None)

            if not data.get("published_at"):
                data["published_at"] = datetime.now()

            role = request.session.get("role")
            user_id = request.session.get("user_id")

            if role != "admin" and is_created:
                author = db.query(Author).filter(Author.user_id == user_id).first()
                if author:
                    data["publisher_id"] = author.id
                else:
                    raise ValidationError("You must have an Author Profile linked to your User to post.")
        finally:
            db.close()

    def on_model_change_error(self, request, form, error):
        db = SessionLocal()
        try:
            if hasattr(form, 'publisher') and form.publisher.data:
                val = form.publisher.data
                if isinstance(val, (int, str)):
                    if isinstance(val, str) and val.isdigit():
                        val = int(val)
                    if isinstance(val, int):
                        author = db.query(Author).get(val)
                        if author:
                            form.publisher.data = author

            if hasattr(form, 'categories') and form.categories.data:
                new_cats = []
                for val in form.categories.data:
                    if isinstance(val, (int, str)):
                        if isinstance(val, str) and val.isdigit():
                            val = int(val)
                        if isinstance(val, int):
                            cat = db.query(Category).get(val)
                            if cat:
                                new_cats.append(cat)
                        else:
                            new_cats.append(val)
                    else:
                        new_cats.append(val)
                form.categories.data = new_cats
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
    form_excluded_columns = [Product.created_at, Product.updated_at, Product.features, Product.why_us, Product.faqs, Product.trusted_by]
    form_overrides = dict(
        hero_subtitle=TextAreaField, 
        id=HiddenField,
        layout=SelectField,     
        layout_type=SelectField 
    )
    
    form_args = { 
        "name": dict(validators=[DataRequired()]),
        "hero_subtitle": dict(render_kw={"rows": 4, "style": "width: 100%;"}),
        "slug": dict(
            label="URL Slug (Auto-generated)", 
            render_kw={"disabled": "disabled"},
            validators=[Optional()]
        ),
        "layout": dict(
            choices=[("default"), ("feature_list")],
            label="Layout Type",
            validators=[Optional()]
        ),
        "layout_type": dict(
            choices=[("default"), ("feature_list")],
            label="Layout Type",
            validators=[Optional()]
        )
    }
    
    column_labels = { Product.hero_title: "Hero Banner Title", Product.hero_subtitle: "Hero Banner Text" }
    
    column_formatters = {
        Product.hero_image: format_image_preview
    }

    async def on_model_change(self, data, model, is_created, request):
        db = SessionLocal()
        try:
            name = data.get("name", "").strip()
            if name:
                query = db.query(Product).filter(Product.name == name)
                
                if not is_created and model.id:
                    query = query.filter(Product.id != model.id)
                
                duplicate = query.first()
                if duplicate:
                    raise ValidationError(f"A product with the name '{name}' already exists.")

            if not is_created and model.slug:
                if "slug" in data:
                    del data["slug"]
            elif name:
                data["slug"] = generate_unique_slug(db, Product, name, model.id if not is_created else None)
        finally:
            db.close()

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

class SocialTrustAdmin(ModelView, model=SocialTrust):
    category = "Partners"
    name = "Social Trust"
    name_plural = "Partner Library"
    icon = "fa-solid fa-handshake"

    column_list = [SocialTrust.logo_url, SocialTrust.name, SocialTrust.sequence]
    column_searchable_list = [SocialTrust.name]
    column_sortable_list = [SocialTrust.sequence]
    
    column_formatters = {
        SocialTrust.logo_url: format_image_preview
    }
    
    column_labels = {
        SocialTrust.logo_url: "Logo Preview"
    }
    
    form_excluded_columns = [SocialTrust.id, SocialTrust.created_at, SocialTrust.updated_at]

class ProductSocialTrustLinkAdmin(ModelView, model=ProductSocialTrustLink):
    category = "Product Manager"
    name = "Product Partner"
    name_plural = "Assign Partners"
    icon = "fa-solid fa-link"

    column_list = [ProductSocialTrustLink.product, ProductSocialTrustLink.partner, ProductSocialTrustLink.sequence]
    column_sortable_list = [ProductSocialTrustLink.product_id, ProductSocialTrustLink.sequence]
    column_formatters = { 
        ProductSocialTrustLink.product: format_relation_link,
        ProductSocialTrustLink.partner: format_relation_link
    }

    form_excluded_columns = [ProductSocialTrustLink.id]
    
    form_ajax_refs = {
        "product": { "fields": ["name"], "order_by": "name", "placeholder": "Select Product..." },
        "partner": { "fields": ["name"], "order_by": "name", "placeholder": "Select Partner..." }
    }

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
        Solution.created_at, Solution.updated_at, 
        Solution.features, Solution.why_us, Solution.faqs, Solution.related_products, Solution.trusted_by
    ]
    
    form_overrides = dict(
        hero_subtitle=TextAreaField,
        core_solution_subtitle=TextAreaField,
        core_benefits_subtitle=TextAreaField,
        id=HiddenField
    )
    
    form_args = { 
        "name": dict(validators=[DataRequired()]),
        "hero_subtitle": dict(render_kw={"rows": 4, "style": "width: 100%;"}),
        "slug": dict(
            label="URL Slug (Auto-generated)", 
            render_kw={"disabled": "disabled"},
            validators=[Optional()]
        ),
        "core_benefits_title": dict(
            label="Benefits Section Title",
            render_kw={"placeholder": "e.g. Benefits"}
        ),
        "core_benefits_subtitle": dict(
            label="Benefits Section Subtitle",
            render_kw={"rows": 3, "style": "width: 100%;"}
        ),
        "core_solution_title": dict(
            label="Solution Section Title",
            render_kw={"placeholder": "e.g. Keunggulan Solusi"}
        ),
        "core_solution_subtitle": dict(
            label="Solution Section Subtitle",
            render_kw={"rows": 3, "style": "width: 100%;"}
        )
    }
    
    column_labels = { 
        Solution.hero_title: "Hero Banner Title", 
        Solution.hero_subtitle: "Hero Banner Text"
    }
    
    column_formatters = {
        Solution.hero_image: format_image_preview,
        Solution.cta_image: format_image_preview
    }

    async def on_model_change(self, data, model, is_created, request):
        db = SessionLocal()
        try:
            name = data.get("name", "").strip()
            if name:
                query = db.query(Solution).filter(Solution.name == name)
                
                if not is_created and model.id:
                    query = query.filter(Solution.id != model.id)
                
                duplicate = query.first()
                if duplicate:
                    raise ValidationError(f"A solution with the name '{name}' already exists.")

            if not is_created and model.slug:
                if "slug" in data:
                    del data["slug"]
            elif name:
                data["slug"] = generate_unique_slug(db, Solution, name, model.id if not is_created else None)
        finally:
            db.close()

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

    column_list = [
        SolutionRelatedProduct.solution, 
        SolutionRelatedProduct.product, 
        SolutionRelatedProduct.icon_url, 
        SolutionRelatedProduct.sequence
    ]
    column_searchable_list = ["solution.name", "product.name"]
    column_formatters = { 
        SolutionRelatedProduct.solution: format_relation_link,
        SolutionRelatedProduct.product: format_relation_link,
        SolutionRelatedProduct.icon_url: format_image_preview
    }
    column_labels = {
        SolutionRelatedProduct.icon_url: "Icon URL (e.g., SVG/PNG)"
    }

    form_excluded_columns = [SolutionRelatedProduct.id, SolutionRelatedProduct.created_at, SolutionRelatedProduct.updated_at]
    form_ajax_refs = {
        "solution": { "fields": ["name"], "order_by": "name", "placeholder": "Which Solution Page?" },
        "product": { "fields": ["name"], "order_by": "name", "placeholder": "Link to which Product?" }
    }

class SolutionSocialTrustLinkAdmin(ModelView, model=SolutionSocialTrustLink):
    category = "Solution Manager"
    name = "Solution Partner"
    name_plural = "Assign Partners"
    icon = "fa-solid fa-link"

    column_list = [SolutionSocialTrustLink.solution, SolutionSocialTrustLink.partner, SolutionSocialTrustLink.sequence]
    column_sortable_list = [SolutionSocialTrustLink.solution_id, SolutionSocialTrustLink.sequence]
    column_formatters = { 
        SolutionSocialTrustLink.solution: format_relation_link,
        SolutionSocialTrustLink.partner: format_relation_link
    }

    form_excluded_columns = [SolutionSocialTrustLink.id]
    
    form_ajax_refs = {
        "solution": { "fields": ["name"], "order_by": "name", "placeholder": "Select Solution..." },
        "partner": { "fields": ["name"], "order_by": "name", "placeholder": "Select Partner..." }
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

class ServicePageAdmin(ModelView, model=ServicePage):
    category = "Service Manager"
    name = "Service Landing Page"
    icon = "fa-solid fa-layer-group"
    
    column_list = [ServicePage.page_name, ServicePage.slug, ServicePage.updated_at]
    column_searchable_list = [ServicePage.page_name, ServicePage.slug, ServicePage.hero_heading]
    
    form_excluded_columns = [
        ServicePage.id, ServicePage.created_at, ServicePage.updated_at,
        ServicePage.focus_items, ServicePage.quick_steps, 
        ServicePage.offerings, ServicePage.methodologies, ServicePage.competencies
    ]
    
    form_overrides = dict(
        hero_tagline=TextAreaField,
        focus_section_desc=TextAreaField,
        quick_step_subheading=TextAreaField,
        quick_step_footer=TextAreaField,
        offering_desc=TextAreaField,
        methodology_desc=TextAreaField,
        methodology_footer=TextAreaField,
        competency_desc=TextAreaField,
        competency_footer=TextAreaField,
        
        quick_step_layout=SelectField,
        methodology_layout=SelectField
    )
    
    form_args = {
        "slug": dict(label="URL Slug (Auto-generated)", render_kw={"disabled": "disabled"}, validators=[Optional()]),
        "page_name": dict(label="Internal Page Name (e.g. Konsultasi)"),
        "hero_tagline": dict(label="Hero Tagline", render_kw={"rows": 3, "style": "width: 100%;"}),
        "hero_heading": dict(label="Hero Heading", render_kw={"style": "width: 100%;"}),
        "hero_bg_image": dict(label="Hero Background Image URL", render_kw={"style": "width: 100%;"}),
        
        "focus_section_tagline": dict(label="Focus Section Tagline", render_kw={"style": "width: 100%;"}),
        "focus_section_heading": dict(label="Focus Section Heading", render_kw={"style": "width: 100%;"}),
        "focus_section_desc": dict(label="Focus Section Description", render_kw={"rows": 4, "style": "width: 100%;"}),
        
        "quick_step_layout": dict(
            choices=[("steps", "Horizontal Steps (1,2,3)"), ("standards_grid", "Standards Grid (Checklists)")],
            label="Quick Step Layout"
        ),
        "quick_step_heading": dict(label="Quick Step Heading", render_kw={"style": "width: 100%;"}),
        "quick_step_subheading": dict(label="Quick Step Subheading", render_kw={"rows": 3, "style": "width: 100%;"}),
        "quick_step_footer": dict(label="Quick Step Footer Text", render_kw={"rows": 3, "style": "width: 100%;"}),

        "offering_heading": dict(label="Offering Section Heading", render_kw={"style": "width: 100%;"}),
        "offering_desc": dict(label="Offering Section Description", render_kw={"rows": 4, "style": "width: 100%;"}),

        "methodology_layout": dict(
            choices=[("timeline", "Vertical Timeline (01, 02)"), ("roles_grid", "Icon Grid (Roles)")],
            label="Methodology Layout"
        ),
        "methodology_heading": dict(label="Methodology Heading", render_kw={"style": "width: 100%;"}),
        "methodology_desc": dict(label="Methodology Description", render_kw={"rows": 4, "style": "width: 100%;"}),
        "methodology_footer": dict(label="Methodology Footer Text", render_kw={"rows": 3, "style": "width: 100%;"}),

        "competency_heading": dict(label="Competency Heading", render_kw={"style": "width: 100%;"}),
        "competency_desc": dict(label="Competency Description", render_kw={"rows": 4, "style": "width: 100%;"}),
        "competency_footer": dict(label="Competency Footer Text", render_kw={"rows": 3, "style": "width: 100%;"}),
    }
    
    column_formatters = {
        ServicePage.hero_bg_image: format_image_preview
    }

    async def on_model_change(self, data, model, is_created, request):
        if data.get("page_name") and not data.get("slug"):
             db = SessionLocal()
             data["slug"] = generate_unique_slug(db, ServicePage, data["page_name"], model.id if not is_created else None)
             db.close()

class ServiceFocusItemAdmin(ModelView, model=ServiceFocusItem):
    category = "Service Manager"
    name = "Focus Grid Item"
    icon = "fa-solid fa-border-all"
    
    column_list = [ServiceFocusItem.service_page, ServiceFocusItem.card_title, ServiceFocusItem.display_order]
    column_searchable_list = ["service_page.page_name", ServiceFocusItem.card_title, ServiceFocusItem.card_desc]
    
    form_excluded_columns = [ServiceFocusItem.id]
    form_overrides = dict(card_desc=TextAreaField)
    
    column_labels = {
        ServiceFocusItem.service_page: "Parent Service Page",
        ServiceFocusItem.card_title: "Title",
        ServiceFocusItem.card_desc: "Description",
        ServiceFocusItem.icon_image: "Icon URL",
        ServiceFocusItem.display_order: "Display Order"
    }

    form_args = { 
        "card_title": dict(render_kw={"style": "width: 100%;"}),
        "card_desc": dict(render_kw={"rows": 4, "style": "width: 100%;"}),
        "icon_image": dict(render_kw={"style": "width: 100%;"}),
        "display_order": dict(render_kw={"style": "width: 100%;"})
    }
    form_ajax_refs = { "service_page": { "fields": ["page_name"], "order_by": "page_name" } }
    
    column_formatters = { ServiceFocusItem.icon_image: format_image_preview }

class ServiceQuickStepAdmin(ModelView, model=ServiceQuickStep):
    category = "Service Manager"
    name = "Quick Step / Standard"
    icon = "fa-solid fa-forward"
    
    column_list = [ServiceQuickStep.service_page, ServiceQuickStep.step_title, ServiceQuickStep.step_order]
    column_searchable_list = ["service_page.page_name", ServiceQuickStep.step_title, ServiceQuickStep.step_desc]
    
    form_excluded_columns = [ServiceQuickStep.id]
    
    form_overrides = dict(step_desc=TextAreaField, checklist=LineSeparatedListField)
    
    column_labels = {
        ServiceQuickStep.service_page: "Parent Service Page",
        ServiceQuickStep.step_label: "Step Number / Label",
        ServiceQuickStep.step_title: "Step Title",
        ServiceQuickStep.step_desc: "Step Description",
        ServiceQuickStep.checklist: "Checklist Items",
        ServiceQuickStep.step_order: "Order Sequence"
    }

    form_args = {
        "step_label": dict(description="Only for 'Steps' layout (e.g. '1.')", render_kw={"style": "width: 100%;"}),
        "step_title": dict(render_kw={"style": "width: 100%;"}),
        "step_desc": dict(render_kw={"rows": 4, "style": "width: 100%;"}),
        "checklist": dict(description="Only for 'Standards' layout. One item per line.", render_kw={"rows": 6, "style": "width: 100%;"}),
        "step_order": dict(render_kw={"style": "width: 100%;"})
    }
    
    form_ajax_refs = { "service_page": { "fields": ["page_name"], "order_by": "page_name" } }

class ServiceOfferingAdmin(ModelView, model=ServiceOffering):
    category = "Service Manager"
    name = "Offering Package"
    icon = "fa-solid fa-box-open"
    
    column_list = [ServiceOffering.service_page, ServiceOffering.title, ServiceOffering.display_order]
    column_searchable_list = ["service_page.page_name", ServiceOffering.title, ServiceOffering.description]
    
    form_excluded_columns = [ServiceOffering.id]
    
    form_overrides = dict(description=TextAreaField, checklist=LineSeparatedListField)
    
    column_labels = {
        ServiceOffering.service_page: "Parent Service Page",
        ServiceOffering.title: "Package Title",
        ServiceOffering.description: "Description",
        ServiceOffering.checklist: "Included Features List",
        ServiceOffering.icon_image: "Icon URL",
        ServiceOffering.highlight_badge: "Badge Text",
        ServiceOffering.button_text: "Button Label",
        ServiceOffering.button_url: "Button Link",
        ServiceOffering.display_order: "Display Order"
    }

    form_args = {
        "title": dict(render_kw={"style": "width: 100%;"}),
        "description": dict(render_kw={"rows": 4, "style": "width: 100%;"}),
        "checklist": dict(render_kw={"rows": 6, "style": "width: 100%;", "placeholder": "Feature 1\nFeature 2"}),
        "highlight_badge": dict(label="Badge Text (e.g. 'POPULAR')", render_kw={"style": "width: 100%;"}),
        "icon_image": dict(render_kw={"style": "width: 100%;"}),
        "button_text": dict(render_kw={"style": "width: 100%;"}),
        "button_url": dict(render_kw={"style": "width: 100%;"}),
        "display_order": dict(render_kw={"style": "width: 100%;"})
    }
    
    column_formatters = { ServiceOffering.icon_image: format_image_preview }
    form_ajax_refs = { "service_page": { "fields": ["page_name"], "order_by": "page_name" } }

class ServiceMethodologyAdmin(ModelView, model=ServiceMethodology):
    category = "Service Manager"
    name = "Methodology / Role"
    icon = "fa-solid fa-timeline"
    
    column_list = [ServiceMethodology.service_page, ServiceMethodology.phase_title, ServiceMethodology.phase_order]
    column_searchable_list = ["service_page.page_name", ServiceMethodology.phase_title, ServiceMethodology.phase_desc]
    
    form_excluded_columns = [ServiceMethodology.id]
    form_overrides = dict(phase_desc=TextAreaField)
    
    column_labels = {
        ServiceMethodology.service_page: "Parent Service Page",
        ServiceMethodology.phase_number: "Phase Number",
        ServiceMethodology.phase_title: "Phase Title",
        ServiceMethodology.phase_desc: "Phase Description",
        ServiceMethodology.icon_image: "Icon URL",
        ServiceMethodology.phase_order: "Phase Order"
    }

    form_args = {
        "phase_number": dict(description="Only for 'Timeline' layout (e.g. '01')", render_kw={"style": "width: 100%;"}),
        "phase_title": dict(render_kw={"style": "width: 100%;"}),
        "phase_desc": dict(render_kw={"rows": 4, "style": "width: 100%;"}),
        "icon_image": dict(description="Only for 'Roles Grid' layout", render_kw={"style": "width: 100%;"}),
        "phase_order": dict(render_kw={"style": "width: 100%;"})
    }
    
    column_formatters = { ServiceMethodology.icon_image: format_image_preview }
    form_ajax_refs = { "service_page": { "fields": ["page_name"], "order_by": "page_name" } }

class ServiceCompetencyAdmin(ModelView, model=ServiceCompetency):
    category = "Service Manager"
    name = "Skill / Competency"
    icon = "fa-solid fa-chart-bar"
    
    column_list = [ServiceCompetency.service_page, ServiceCompetency.skill_name, ServiceCompetency.percentage_value, ServiceCompetency.rank_order]
    column_searchable_list = ["service_page.page_name", ServiceCompetency.skill_name]
    
    form_excluded_columns = [ServiceCompetency.id]
    form_ajax_refs = { "service_page": { "fields": ["page_name"], "order_by": "page_name" } }

    column_labels = {
        ServiceCompetency.service_page: "Parent Service Page",
        ServiceCompetency.skill_name: "Skill Name",
        ServiceCompetency.percentage_value: "Proficiency (%)",
        ServiceCompetency.rank_order: "Display Order"
    }
    
    form_args = {
        "skill_name": dict(render_kw={"style": "width: 100%;"}),
        "percentage_value": dict(render_kw={"style": "width: 100%;"}),
        "rank_order": dict(render_kw={"style": "width: 100%;"})
    }

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

    admin.add_view(SocialTrustAdmin)
    admin.add_view(ProductSocialTrustLinkAdmin)

    admin.add_view(SolutionAdmin)
    admin.add_view(SolutionFeatureAdmin)
    admin.add_view(SolutionWhyUsAdmin)
    admin.add_view(SolutionFAQAdmin)
    admin.add_view(SolutionRelatedProductAdmin)
    admin.add_view(SolutionSocialTrustLinkAdmin)

    admin.add_view(ServicePageAdmin)
    admin.add_view(ServiceFocusItemAdmin)
    admin.add_view(ServiceQuickStepAdmin)
    admin.add_view(ServiceOfferingAdmin)
    admin.add_view(ServiceMethodologyAdmin)
    admin.add_view(ServiceCompetencyAdmin)

    return admin