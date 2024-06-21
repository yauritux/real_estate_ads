{
    "name": "Real Estate Ads",
    "version": "1.0",
    "website": "https://bisnisin.asia",
    "author": "Yauri Attamimi",
    "description": """
        Real Estate module to show available properties
    """,
    "category": "Sales",
    "depends": ["base"],
    "data": [
        # Security Group Access
        "security/ir.model.access.csv",
        "security/res_groups.xml",
        "security/model_access.xml",
        "security/ir_rule.xml",

        # Views
        "views/property_view.xml",
        "views/property_type_view.xml",
        "views/property_tag_view.xml",
        "views/property_offer_view.xml",
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