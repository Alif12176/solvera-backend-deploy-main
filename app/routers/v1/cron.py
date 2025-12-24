from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from bs4 import BeautifulSoup
import vercel_blob
import os
from app.models.blog import Article
from app.models.product import Product, ProductFeature, ProductWhyUs
from app.models.solutions import Solution, SolutionWhyUs, SolutionRelatedProduct
from app.models.social_trust import SocialTrust
from app.models.service import (
    ServicePage, 
    ServiceFocusItem, 
    ServiceMethodology, 
    ServiceOffering
)

router = APIRouter()

@router.get("/cleanup-images")
async def cleanup_unused_images(
    request: Request,
    db: Session = Depends(get_db)
):

    auth_header = request.headers.get("Authorization")
    cron_secret = os.getenv('CRON_SECRET')
    expected_secret = f"Bearer {cron_secret}"
    
    if cron_secret and auth_header != expected_secret:
         raise HTTPException(status_code=401, detail="Unauthorized")

    active_urls = set()

    articles = db.query(Article).all()
    for article in articles:
        if article.image_url:
            active_urls.add(article.image_url)
        
        if article.content:
            try:
                soup = BeautifulSoup(article.content, "html.parser")
                for img in soup.find_all("img"):
                    src = img.get("src")
                    if src and "public.blob.vercel-storage.com" in src:
                        active_urls.add(src)
            except Exception:
                pass 

    products = db.query(Product).all()
    for p in products:
        if p.hero_image: active_urls.add(p.hero_image)
        if p.cta_image: active_urls.add(p.cta_image)
    
    p_features = db.query(ProductFeature).all()
    for pf in p_features:
        if pf.image_url: active_urls.add(pf.image_url)
        
    p_why_us = db.query(ProductWhyUs).all()
    for pw in p_why_us:
        if pw.icon: active_urls.add(pw.icon)

    solutions = db.query(Solution).all()
    for s in solutions:
        if s.hero_image: active_urls.add(s.hero_image)
        if s.cta_image: active_urls.add(s.cta_image)
        
    s_why_us = db.query(SolutionWhyUs).all()
    for sw in s_why_us:
        if sw.icon: active_urls.add(sw.icon)

    s_related = db.query(SolutionRelatedProduct).all()
    for sr in s_related:
        if sr.icon_url: active_urls.add(sr.icon_url)

    services = db.query(ServicePage).all()
    for svc in services:
        if svc.hero_bg_image: active_urls.add(svc.hero_bg_image)
    
    svc_focus = db.query(ServiceFocusItem).all()
    for item in svc_focus:
        if item.icon_image: active_urls.add(item.icon_image)

    svc_offerings = db.query(ServiceOffering).all()
    for item in svc_offerings:
        if item.icon_image: active_urls.add(item.icon_image)

    svc_methodologies = db.query(ServiceMethodology).all()
    for item in svc_methodologies:
        if item.icon_image: active_urls.add(item.icon_image)

    partners = db.query(SocialTrust).all()
    for p in partners:
        if p.logo_url: active_urls.add(p.logo_url)

    try:
        blob_response = vercel_blob.list() 
        all_blobs = blob_response.get('blobs', [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch blobs from Vercel: {str(e)}")

    blobs_to_delete = []
    
    for blob in all_blobs:
        if blob['url'] not in active_urls:
            blobs_to_delete.append(blob['url'])

    deleted_count = 0
    if blobs_to_delete:
        try:
            vercel_blob.delete(blobs_to_delete)
            deleted_count = len(blobs_to_delete)
        except Exception as e:
            print(f"Error deleting blobs: {e}")

    return {
        "success": True,
        "message": "Cleanup execution complete",
        "stats": {
            "active_images_in_db": len(active_urls),
            "total_files_in_blob": len(all_blobs),
            "deleted_files": deleted_count
        },
        "deleted_urls": blobs_to_delete
    }