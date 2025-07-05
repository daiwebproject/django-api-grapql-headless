import graphene
from graphene_file_upload.scalars import Upload
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from oscar.core.loading import get_model
from api.types.product import ProductType, ProductImageType
from api.utils.permissions import staff_required
import uuid
import os

Product = get_model('catalogue', 'Product')
ProductImage = get_model('catalogue', 'ProductImage')

class UploadProductImage(graphene.Mutation):
    class Arguments:
        product_id = graphene.ID(required=True)
        image = Upload(required=True)
        caption = graphene.String()
        display_order = graphene.Int()
    
    product_image = graphene.Field(ProductImageType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)
    
    @staff_required
    def mutate(self, info, product_id, image, caption=None, display_order=0):
        try:
            product = Product.objects.get(id=product_id)
            
            # Validate file type
            allowed_types = ['image/jpeg', 'image/png', 'image/webp']
            if image.content_type not in allowed_types:
                return UploadProductImage(
                    product_image=None,
                    success=False,
                    errors=["Only JPEG, PNG and WebP images are allowed"]
                )
            
            # Validate file size (5MB max)
            if image.size > 5 * 1024 * 1024:
                return UploadProductImage(
                    product_image=None,
                    success=False,
                    errors=["File size too large. Maximum 5MB allowed"]
                )
            
            # Generate unique filename
            ext = os.path.splitext(image.name)[1]
            filename = f"products/{product.slug}/{uuid.uuid4()}{ext}"
            
            # Save file
            file_path = default_storage.save(filename, ContentFile(image.read()))
            
            # Create ProductImage instance
            product_image = ProductImage.objects.create(
                product=product,
                original=file_path,
                caption=caption or '',
                display_order=display_order
            )
            
            return UploadProductImage(
                product_image=product_image,
                success=True,
                errors=[]
            )
            
        except Product.DoesNotExist:
            return UploadProductImage(
                product_image=None,
                success=False,
                errors=["Product not found"]
            )
        except Exception as e:
            return UploadProductImage(
                product_image=None,
                success=False,
                errors=[str(e)]
            )

class DeleteProductImage(graphene.Mutation):
    class Arguments:
        image_id = graphene.ID(required=True)
    
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)
    
    @staff_required
    def mutate(self, info, image_id):
        try:
            image = ProductImage.objects.get(id=image_id)
            
            # Delete file from storage
            if image.original:
                default_storage.delete(image.original.name)
            
            # Delete database record
            image.delete()
            
            return DeleteProductImage(success=True, errors=[])
            
        except ProductImage.DoesNotExist:
            return DeleteProductImage(success=False, errors=["Image not found"])
        except Exception as e:
            return DeleteProductImage(success=False, errors=[str(e)])

class UploadMutation:
    upload_product_image = UploadProductImage.Field()
    delete_product_image = DeleteProductImage.Field()