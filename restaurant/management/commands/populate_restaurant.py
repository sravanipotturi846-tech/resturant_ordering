from django.core.management.base import BaseCommand
from restaurant.models import Category, MenuItem, Testimonial, Reservation, Order, OrderItem
import datetime
from decimal import Decimal


class Command(BaseCommand):
    help = 'Populates luxury restaurant mock data for menu, reviews, and sample bookings.'

    def handle(self, *args, **options):
        self.stdout.write("Seeding luxury restaurant data...")

        # Clear existing to avoid duplicate issues
        Category.objects.all().delete()
        MenuItem.objects.all().delete()
        Testimonial.objects.all().delete()

        # 1. Categories
        cat_starters = Category.objects.create(
            name="Starters & Small Plates",
            description="Exquisite opening notes curated with seasonal terroir and delicate textures.",
            order=1,
            icon="appetizer"
        )
        cat_signatures = Category.objects.create(
            name="Chef's Signatures",
            description="Flagship culinary creations showcasing avant-garde precision and rare ingredients.",
            order=2,
            icon="award"
        )
        cat_mains = Category.objects.create(
            name="Mains & Grill",
            description="Prime dry-aged meats, wild ocean catches, and harvest vegetables flame-finished.",
            order=3,
            icon="flame"
        )
        cat_desserts = Category.objects.create(
            name="Artisan Desserts",
            description="Sculpted sweet masterworks paired with single-origin chocolates and botanical coulis.",
            order=4,
            icon="cake"
        )
        cat_cellar = Category.objects.create(
            name="Craft Cocktails & Cellar",
            description="Mixology elixirs infused tableside and reserve vintages from legendary estates.",
            order=5,
            icon="wine"
        )

        # 2. Menu Items
        dishes = [
            # Starters
            {
                "category": cat_starters,
                "name": "Wagyu Carpaccio Royale",
                "description": "Thinly shaved A5 Miyazaki Wagyu, caper emulsion, pickled shallots, shaved black winter truffle, and 24-month aged Parmigiano crisp.",
                "price": Decimal("28.00"),
                "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=800&q=80",
                "calories": 390,
                "prep_time_minutes": 12,
                "rating": Decimal("4.9"),
                "is_chef_special": True,
                "is_gluten_free": True,
            },
            {
                "category": cat_starters,
                "name": "Pan-Seared Hokkaido Scallops",
                "description": "Caramelized diver scallops set on sweet parsnip purée, crispy jamón ibérico crumbs, and Meyer lemon brown butter sauce.",
                "price": Decimal("26.50"),
                "image_url": "https://images.unsplash.com/photo-1532550907401-a500c9a57435?auto=format&fit=crop&w=800&q=80",
                "calories": 340,
                "prep_time_minutes": 15,
                "rating": Decimal("4.8"),
                "is_gluten_free": True,
            },
            {
                "category": cat_starters,
                "name": "Wild Morel & Black Truffle Velouté",
                "description": "Velvety forest mushroom soup infused with Périgord truffle cream, herb brioche crouton, and chive oil drops.",
                "price": Decimal("21.00"),
                "image_url": "https://images.unsplash.com/photo-1547592166-23ac45744acd?auto=format&fit=crop&w=800&q=80",
                "calories": 280,
                "prep_time_minutes": 10,
                "rating": Decimal("4.7"),
                "is_vegetarian": True,
            },
            {
                "category": cat_starters,
                "name": "Burrata Artigianale Pugliese",
                "description": "Heirloom sun-ripened tomatoes, aged Modena balsamic pearls, roasted pine nut praline, and cold-pressed Sicilian olive oil.",
                "price": Decimal("22.50"),
                "image_url": "https://images.unsplash.com/photo-1592417817098-8f3d6910985c?auto=format&fit=crop&w=800&q=80",
                "calories": 410,
                "prep_time_minutes": 10,
                "rating": Decimal("4.9"),
                "is_vegetarian": True,
                "is_gluten_free": True,
            },

            # Chef Signatures
            {
                "category": cat_signatures,
                "name": "Chilean Sea Bass Glacier",
                "description": "Glazed with white miso and mirin, served over baby bok choy, lotus root crisp, and a lemongrass dashi reduction.",
                "price": Decimal("48.00"),
                "image_url": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?auto=format&fit=crop&w=800&q=80",
                "calories": 520,
                "prep_time_minutes": 22,
                "rating": Decimal("5.0"),
                "is_chef_special": True,
                "is_gluten_free": True,
            },
            {
                "category": cat_signatures,
                "name": "Maine Lobster & Saffron Risotto",
                "description": "Acquerello aged carnaroli rice simmered in shellfish broth with butter-poached Maine lobster claw, saffron pistils, and sea asparagus.",
                "price": Decimal("54.00"),
                "image_url": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?auto=format&fit=crop&w=800&q=80",
                "calories": 610,
                "prep_time_minutes": 25,
                "rating": Decimal("4.9"),
                "is_chef_special": True,
                "is_gluten_free": True,
            },
            {
                "category": cat_signatures,
                "name": "Canard de Barbarie à l'Orange Sanguine",
                "description": "Slow-roasted spiced duck breast, blood orange and star anise reduction, parsnip mousse, and glazed baby rainbow carrots.",
                "price": Decimal("44.00"),
                "image_url": "https://images.unsplash.com/photo-1514944298352-f3e9c991e605?auto=format&fit=crop&w=800&q=80",
                "calories": 680,
                "prep_time_minutes": 20,
                "rating": Decimal("4.9"),
                "is_chef_special": True,
            },

            # Mains & Grill
            {
                "category": cat_mains,
                "name": "Prime Dry-Aged Filet Mignon (8oz)",
                "description": "45-day dry-aged Black Angus tenderloin, bone marrow butter, potato mousseline with black garlic jus, and charred asparagus.",
                "price": Decimal("52.00"),
                "image_url": "https://images.unsplash.com/photo-1558030006-450675393462?auto=format&fit=crop&w=800&q=80",
                "calories": 740,
                "prep_time_minutes": 24,
                "rating": Decimal("4.9"),
                "is_gluten_free": True,
            },
            {
                "category": cat_mains,
                "name": "Handmade Black Truffle Tagliolini",
                "description": "Egg pasta tossed in Normandy butter and aged pecorino, generously crowned with shaved fresh Norcia truffles.",
                "price": Decimal("38.00"),
                "image_url": "https://images.unsplash.com/photo-1556761223-4c4282c73f77?auto=format&fit=crop&w=800&q=80",
                "calories": 590,
                "prep_time_minutes": 16,
                "rating": Decimal("4.8"),
                "is_vegetarian": True,
            },
            {
                "category": cat_mains,
                "name": "Herb-Crusted Colorado Lamb Rack",
                "description": "Rosemary and Dijon mustard herb crumb, smoked polenta cake, confit pearl onions, and natural rosemary lamb reduction.",
                "price": Decimal("49.00"),
                "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=800&q=80",
                "calories": 710,
                "prep_time_minutes": 26,
                "rating": Decimal("4.9"),
            },
            {
                "category": cat_mains,
                "name": "Charred Romanesco & Romesco (Vegan)",
                "description": "Whole-roasted romesco cauliflower florets over charred almond romesco sauce, pomegranate molasses, and garden herb oil.",
                "price": Decimal("32.00"),
                "image_url": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=800&q=80",
                "calories": 380,
                "prep_time_minutes": 18,
                "rating": Decimal("4.7"),
                "is_vegetarian": True,
                "is_vegan": True,
                "is_gluten_free": True,
            },

            # Desserts
            {
                "category": cat_desserts,
                "name": "Valrhona Guanaja Chocolate Dome",
                "description": "70% single-origin dark chocolate sphere, warm salted caramel pour-over, hazelnut feuilletine, and gold leaf flake.",
                "price": Decimal("18.00"),
                "image_url": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=800&q=80",
                "calories": 490,
                "prep_time_minutes": 12,
                "rating": Decimal("5.0"),
                "is_chef_special": True,
                "is_vegetarian": True,
            },
            {
                "category": cat_desserts,
                "name": "Madagascar Vanilla Mille-Feuille",
                "description": "Crisp caramelized puff pastry layers filled with Bourbon vanilla bean diplomate cream and raspberry gelee droplets.",
                "price": Decimal("16.50"),
                "image_url": "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=800&q=80",
                "calories": 420,
                "prep_time_minutes": 10,
                "rating": Decimal("4.8"),
                "is_vegetarian": True,
            },
            {
                "category": cat_desserts,
                "name": "Meyer Lemon & Yuzu Sphere",
                "description": "Candied lemon curd, almond sable crumble, toasted Italian meringue peaks, and fragrant yuzu sorbet.",
                "price": Decimal("16.00"),
                "image_url": "https://images.unsplash.com/photo-1587314168485-3236d6710814?auto=format&fit=crop&w=800&q=80",
                "calories": 360,
                "prep_time_minutes": 10,
                "rating": Decimal("4.8"),
                "is_vegetarian": True,
                "is_gluten_free": True,
            },

            # Cellar & Cocktails
            {
                "category": cat_cellar,
                "name": "Smoked Cedar Old Fashioned",
                "description": "Woodford Reserve bourbon, Demerara sugar cube, Angostura bitters, expressed flamed orange peel, served in cedar smoke bell.",
                "price": Decimal("22.00"),
                "image_url": "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?auto=format&fit=crop&w=800&q=80",
                "calories": 180,
                "prep_time_minutes": 6,
                "rating": Decimal("4.9"),
                "is_chef_special": True,
                "is_vegan": True,
                "is_gluten_free": True,
            },
            {
                "category": cat_cellar,
                "name": "Golden Hour French 75",
                "description": "Monkey 47 botanical gin, fresh lemon juice, champagne syrup, topped with Veuve Clicquot champagne and edible 24k gold flakes.",
                "price": Decimal("24.00"),
                "image_url": "https://images.unsplash.com/photo-1551024709-8f23befc6f87?auto=format&fit=crop&w=800&q=80",
                "calories": 160,
                "prep_time_minutes": 5,
                "rating": Decimal("4.9"),
                "is_vegan": True,
                "is_gluten_free": True,
            },
            {
                "category": cat_cellar,
                "name": "Château Margaux Premier Grand Cru (Glass)",
                "description": "Vintage 2015 Bordeaux. Velvety tannins with deep aromas of blackcurrant, cedarwood, violet petals, and graphite notes.",
                "price": Decimal("65.00"),
                "image_url": "https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?auto=format&fit=crop&w=800&q=80",
                "calories": 140,
                "prep_time_minutes": 3,
                "rating": Decimal("5.0"),
                "is_vegan": True,
                "is_gluten_free": True,
            },
        ]

        for item_data in dishes:
            MenuItem.objects.create(**item_data)

        # 3. Testimonials
        reviews = [
            {
                "author_name": "Eleanor Vance",
                "designation": "Michelin Guide Inspector & Food Critic",
                "rating": 5,
                "comment": "An astonishing symphony of flavors. The Chilean Sea Bass and Saffron Lobster Risotto redefine contemporary haute cuisine. The ambiance is sheer luxury.",
                "dish_highlight": "Chilean Sea Bass Glacier",
                "is_featured": True
            },
            {
                "author_name": "Marcus Aurelius Sterling",
                "designation": "International Gastronomy Society",
                "rating": 5,
                "comment": "From the sommelier's bespoke wine pairing to the theater of the Smoked Cedar Old Fashioned, every single detail was masterfully executed.",
                "dish_highlight": "Smoked Cedar Old Fashioned",
                "is_featured": True
            },
            {
                "author_name": "Sophia Laurent",
                "designation": "Epicurean Journal Paris",
                "rating": 5,
                "comment": "The Wagyu Royale and Valrhona Dome are celestial. The service is unobtrusive, polite, and deeply knowledgeable. A must-visit culinary destination.",
                "dish_highlight": "Wagyu Carpaccio Royale",
                "is_featured": True
            }
        ]

        for review_data in reviews:
            Testimonial.objects.create(**review_data)

        # 4. Sample Reservation
        Reservation.objects.create(
            customer_name="Lord Julian Thorne",
            email="julian.thorne@estate.co.uk",
            phone="+1 (555) 234-5678",
            date=datetime.date.today() + datetime.timedelta(days=1),
            time_slot="20:00",
            guests=4,
            seating_area="chef_counter",
            special_requests="Anniversary dinner. Would appreciate window view and sommelier pairings.",
            status="confirmed"
        )

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {len(dishes)} dishes, {len(reviews)} reviews, and sample bookings!"))
