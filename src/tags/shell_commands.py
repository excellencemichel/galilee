""""
# Shell session 1
# python manage.py shell
"""


from tags.models import Tag 

qs = Tag.objects.all()
print(qs)
black = Tag.objects.last()
black.title
black.slug


black.products
"""
Returns:
<django.db.models.fields.related_descriptors.create_forward_many_to_many_manager.<locals>.ManyRelatedManager object at 0x7fee55554518>
"""





black.products.all()
""" This is an actual queryset of PRODUCTS
Much like Products.objectts.all(), but in this case it's ALL of the products that are related to the "Black" tag
"""

black.products.all().first()
"""
returns the first instance, if any
"""
exit()



"""
# Shell session 2
# python manage.py shell
"""

from products.models import Product

qs = Product.objectts.all()
print(qs)
tshirt = qs.first()
tshirt.title
tshirt.description

tshirt.tag 
"""
Raises an error because the Product model dosen't have a field "tag"
"""

tshirt.tags
"""
Raises an error because the product models dosen't have a field "tags"
"""

tshirt.tag_set
"""
This works because the Tag model has the "products" field with the ManyToManyField to Product
<django.db.models.fields.related_descriptors.create_forward_many_to_many_manager.<locals>.ManyRelatedManager object at 0x7fee55575c18>
"""

tshirt.tag_set.all()
"""
Returns an actual Queryset of the Tag model related to this product
<QuerySet [<Tag: T-Shirt>, <Tag: T-Shirt>, <Tag: Red>]>
"""

tshirt.tag_set.filter(title__icontains="black")
"""
This works

"""

