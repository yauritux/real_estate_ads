{
    "name": "Real Estate Ads",
    "version": "1.0",
    "website": "https://bisnisin.asia",
    "author": "Yauri Attamimi",
    "description": """
        Real Estate module to show available properties
    """,
    "category": "Sales",
    "depends": [],
    "data": [
        "security/ir.model.access.csv",
        "views/property_view.xml",
        "views/property_type_view.xml",
        "views/property_tag_view.xml",
        "views/menu_items.xml",

        # Data Files
        "data/property_type.xml",
        "data/estate.property.tag.csv"
    ],
    "demo": [],
    "installable": True,
    "application": True,
    "license": "GPL-3"
}