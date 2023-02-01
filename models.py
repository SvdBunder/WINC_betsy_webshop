# Models go here
from peewee import *

db = SqliteDatabase("betsy_webshop")

# peewee-docs adviseren om geen non-integer primary keys te gebruiken, voor alle modellen wordt daarom gebruik gemaakt
# van het automatisch gegenereerd id als primary key.


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    # bijkomend argument om username niet als primary key aan te merken:
    # er kunnen meerdere personen zijn met dezelfde naam.
    username = CharField()
    hometown = CharField()
    address = CharField()
    bank_account = CharField()


class Tag(BaseModel):
    tagname = CharField(unique=True)


class Product(BaseModel):
    # uitgangspunt: een product kan door meerdere sellers worden gemaakt en verkocht (bijvoorbeeld een "knitted blue sweater"), dus de productnaam is niet uniek.
    productname = CharField()
    description = TextField()
    price_per_unit = DecimalField(
        decimal_places=2, auto_round=True, constraints=[Check("price_per_unit > 0")]
    )
    amount_in_stock = IntegerField(
        constraints=[Check("amount_in_stock >= 0")], default=0
    )
    seller = ForeignKeyField(User, backref="products")

    class Meta:
        # een productnaam mag maar 1x aan een seller zijn gekoppeld
        indexes = ((("productname", "seller"), True),)


class ProductTag(BaseModel):
    product = ForeignKeyField(Product)
    tag = ForeignKeyField(Tag)

    class Meta:
        indexes = (
            (("product", "tag"), True),
        )  # tag mag maar 1x worden toegekend aan een product


class Transaction(BaseModel):
    buyer = ForeignKeyField(User)
    product_purchased = ForeignKeyField(Product)
    amount_purchased = IntegerField(constraints=[Check("amount_purchased > 0")])
