__winc_id__ = "d7b474e9b3a54d23bca54879a4f1855b"
__human_name__ = "Betsy Webshop"

import models
from peewee import *
from spellchecker import SpellChecker


def search(term):
    spelling = SpellChecker()
    # controleren of zoekterm juiste spelling heeft
    if spelling[term]:
        products = models.Product.select().where(
            models.Product.productname.contains(
                term.lower()
            )  # productname wordt in lowercase opgeslagen
            | fn.lower(models.Product.description).contains(
                term.lower()
            )  # de description kan uppercase bevatten => omzetten in lowercase voor de vergelijking
        )
        print(f"Products found for {term}:")

    # indien foute spelling dan worden alle mogelijke woorden gegenereerd en langsgelopen tot er een match is met een woord in productname of description
    else:

        possible_matches = spelling.candidates(term)
        for word in possible_matches:
            products = models.Product.select().where(
                models.Product.productname.contains(
                    word.lower()
                )  # productname wordt in lowercase opgeslagen
                | fn.lower(models.Product.description).contains(
                    word.lower()
                )  # de description kan uppercase bevatten => omzetten in lowercase voor de vergelijking
            )
            if products:
                print(f"Do you mean {word}? \nProducts found for {word}:")
                break
            else:
                continue

    if products:

        return products
    else:
        return print("No matches found in the catalog.")


def list_user_products(user_id):
    # bij "user_id" kan zowel het automatisch gegenereerde id nummer als de username worden ingevuld.
    seller = ()

    # query om seller op te halen o.b.v. id (= integer) of username
    if type(user_id) is int:
        try:
            seller = models.User.get_by_id(user_id)

        except DoesNotExist:
            return "User does not exist"
    else:
        try:
            seller = models.User.get(fn.lower(models.User.username) == user_id.lower())

        except DoesNotExist:
            return "User does not exist"

    products = (
        models.Product.select(models.Product, models.User)
        .join(models.User)
        .where(models.User.username == seller.username)
    )

    return products


def list_products_per_tag(tag_id):
    # bij "tag_id" kan zowel het automatisch gegenereerde id nummer als de tagname worden ingevuld.
    tag = ()
    # query om tag op te halen o.b.v. id (= integer) of tagname
    if type(tag_id) is int:
        try:
            tag = models.Tag.get_by_id(tag_id)

        except DoesNotExist:
            return "Tag does not exist"
    else:
        try:
            tag = models.Tag.get(fn.lower(models.Tag.tagname) == tag_id.lower())

        except DoesNotExist:
            return "Tag does not exist"

    products = (
        models.Product.select()
        .join(models.ProductTag)
        .join(models.Tag)
        .where(models.Tag.tagname == tag.tagname)
    )
    return products


def add_product_to_catalog(user_id, product, description, price_per_unit, list_of_tags):
    # bij user_id en tag_id kunnen zowel het automatisch gegenereerde id nummer als de username of tagname worden ingevuld.

    # product aanmaken; ophalen seller middels query o.b.v. id (=integer) of username
    seller = ()

    if type(user_id) is int:
        try:
            seller = models.User.get_by_id(user_id)

        except DoesNotExist:
            return print(f"{user_id}: user does not exist")
    else:
        try:
            seller = models.User.get(fn.lower(models.User.username) == user_id.lower())

        except DoesNotExist:
            return print(f"{user_id}: user does not exist")

    try:
        new_product = models.Product.create(
            productname=product.lower(),
            description=description,
            price_per_unit=price_per_unit,
            seller=seller,
        )
    except IntegrityError:
        return print(f"{product}: product is already in the catalog of chosen seller")

    # tags toevoegen; ophalen tag middels query o.b.v. id (=integer) of tagname
    message = []
    for item in list_of_tags:
        tag = ()

        if type(item) is int:
            try:
                tag = models.Tag.get_by_id(item)

            except DoesNotExist:
                message.append(f"{item}: tag does not exist")
                continue
        else:
            try:
                tag = models.Tag.get(fn.lower(models.Tag.tagname) % item.lower())

            except DoesNotExist:
                tag = models.Tag.create(tagname=item.lower())
                message.append(f"{item}: tag was created")
                continue
        try:
            new_tag = models.ProductTag(product=new_product, tag=tag)
            new_tag.save()

        except IntegrityError:
            message.append(f"{item}: product already had this tag")
            continue
    if message:
        return print("\n".join(message))


def update_stock(product_id, new_quantity):
    # aanname: de webpagina is dusdanig ingericht dat het id nummer van het product wordt geretourneerd, deze is uniek per seller.
    # als dat niet het geval zou zijn, zou ook de seller aangegeven moeten worden om te zorgen dat het juiste product wordt geselecteerd.

    # controleren of gekozen product bestaat
    try:
        product = models.Product.get_by_id(product_id)
        # product bijwerken
        product.amount_in_stock = new_quantity
        product.save()

    except DoesNotExist:
        return print("Product does not exist")


def purchase_product(product_id, buyer_id, quantity):
    # aanname: de webpagina is dusdanig ingericht dat het id nummer van het product wordt geretourneerd, deze is uniek per seller.
    # als dat niet het geval zou zijn, zou ook de seller aangegeven moeten worden om te zorgen dat het juiste product wordt geselecteerd.
    # bij buyer_id kunnen zowel het automatisch gegenereerde id nummer als de username worden ingevuld.
    product = ()
    buyer = ()
    # query om het product op te halen o.b.v. id (= integer) of productname
    try:
        product = models.Product.get_by_id(product_id)

    except DoesNotExist:
        return print("Product does not exist")

    # query om de user op te halen o.b.v. id (= integer) of username
    if type(buyer_id) is int:
        try:
            buyer = models.User.get_by_id(buyer_id)

        except DoesNotExist:
            return print("User does not exist")
    else:
        try:
            buyer = models.User.get(fn.lower(models.User.username) == buyer_id.lower())

        except DoesNotExist:
            return print("User does not exist")

    # de transactie verwerken
    purchase = models.Transaction(
        buyer=buyer,
        product_purchased=product,
        amount_purchased=quantity,
    )
    purchase.save()

    # de "amount_in_stock" bijwerken met de transactie
    new_stock = product.amount_in_stock - quantity
    update_stock(product_id=product.id, new_quantity=new_stock)


def remove_product(product_id):
    # aanname: de webpagina is dusdanig ingericht dat het id nummer van het product wordt geretourneerd, deze is uniek per seller.
    # als dat niet het geval zou zijn, zou ook de seller aangegeven moeten worden om te zorgen dat enkel het product van die seller wordt verwijderd.

    try:
        product = models.Product.get_by_id(product_id)
        name_product = product.productname
        seller_product = product.seller.username
        product.delete_instance()
        return print(
            f"{name_product} of seller {seller_product} was removed from the catalog"
        )

    except DoesNotExist:
        return print("Product does not exist in the catalog")


def populate_test_database():
    models.db.connect()
    models.db.drop_tables(
        [models.User, models.Tag, models.Product, models.Transaction, models.ProductTag]
    )  # verwijderd de tabellen wanneer de functie opnieuw wordt geactiveerd om weer met "verse" testgegevens te kunnen werken.
    models.db.create_tables(
        [models.User, models.Tag, models.Product, models.Transaction, models.ProductTag]
    )

    data_users = [
        ("Doreen Dolittle", "San Fransisco", "Underhill 145", "BANK123456"),
        ("Jacobus Jazegger", "Detroit", "Lincoln lane 99", "BANK598795"),
        ("Thera Travaille", "New Orleans", "Harbourside 66", "BANK333333"),
    ]

    for username, hometown, address, bank in data_users:
        user = models.User.create(
            username=username, hometown=hometown, address=address, bank_account=bank
        )

    data_tags = [
        "patched up clothes",
        "knitted clothes",
        "winter clothes",
        "black clothes",
        "recycled materials",
        "woolen underwear",
    ]

    for product_tag in data_tags:
        tag = models.Tag.create(tagname=product_tag)

    data_products = [
        (
            "knitted black undergarment",
            "black warm woolen socks and underpants",
            6.25,
            "Thera Travaille",
            6,
            ["knitted clothes", "woolen underwear", "black clothes"],
        ),
        (
            "knitted blue undergarment",
            "blue warm woolen socks and underpants",
            6.25,
            "Thera Travaille",
            6,
            ["knitted clothes", "woolen underwear"],
        ),
        (
            "oceanwide black socks",
            "made from black colored recycled fishnets, keeps your feet from getting smelly",
            3.50,
            "Jacobus Jazegger",
            2,
            ["black clothes", "recycled materials"],
        ),
        (
            "knitted multi color sweater",
            "a sweater made of the warmest and softest fabric",
            40.00,
            "Thera Travaille",
            3,
            ["knitted clothes", "winter clothes"],
        ),
        (
            "heavy duty socks",
            "socks are given a new life patching up the heels with a strip of leather",
            4.75,
            "Doreen Dolittle",
            15,
            ["patched up clothes", "recycled materials"],
        ),
    ]

    for productname, description, price, seller, quantity, taglist in data_products:
        user = models.User.get(models.User.username == seller)
        product = models.Product.create(
            productname=productname,
            description=description,
            price_per_unit=price,
            seller=user,
            amount_in_stock=quantity,
        )
        for tagged in taglist:
            tag = models.Tag.get(models.Tag.tagname == tagged)
            models.ProductTag.create(product=product, tag=tag)
