"""Recipe data generator with realistic, semantically meaningful content."""

import random
from datetime import datetime
from typing import Any
from uuid import UUID


class RecipeDataGenerator:
    """Generate realistic recipe data for database seeding."""

    # Recipe templates organized by category
    BREAKFAST_RECIPES = [
        {
            "name": "Classic French Toast",
            "description": "Golden, crispy French toast with cinnamon and vanilla",
            "cuisine_type": "French",
            "difficulty": "easy",
            "prep_time": 10,
            "cook_time": 15,
            "servings": 4,
            "diet_types": ["vegetarian"],
            "ingredients": [
                {"name": "eggs", "quantity": 4, "unit": "whole"},
                {"name": "milk", "quantity": 0.5, "unit": "cup"},
                {"name": "vanilla extract", "quantity": 1, "unit": "tsp"},
                {"name": "cinnamon", "quantity": 0.5, "unit": "tsp"},
                {"name": "bread slices", "quantity": 8, "unit": "slices"},
                {"name": "butter", "quantity": 2, "unit": "tbsp"},
                {"name": "maple syrup", "quantity": 0.25, "unit": "cup", "notes": "for serving"},
            ],
            "instructions": {
                "steps": [
                    "Whisk together eggs, milk, vanilla, and cinnamon in a shallow bowl",
                    "Heat butter in a large skillet over medium heat",
                    "Dip bread slices in egg mixture, coating both sides",
                    "Cook until golden brown, about 3 minutes per side",
                    "Serve warm with maple syrup and fresh berries"
                ],
                "tips": ["Use day-old bread for best texture", "Keep cooked slices warm in 200F oven"]
            },
            "nutritional_info": {
                "calories": 320,
                "protein_g": 12,
                "carbohydrates_g": 42,
                "fat_g": 11,
                "fiber_g": 2,
                "sugar_g": 18,
                "sodium_mg": 380,
                "cholesterol_mg": 195
            }
        },
        {
            "name": "Avocado Toast with Poached Egg",
            "description": "Creamy avocado on toasted sourdough topped with perfectly poached egg",
            "cuisine_type": "American",
            "difficulty": "medium",
            "prep_time": 10,
            "cook_time": 10,
            "servings": 2,
            "diet_types": ["vegetarian"],
            "ingredients": [
                {"name": "sourdough bread", "quantity": 2, "unit": "slices"},
                {"name": "ripe avocados", "quantity": 1, "unit": "whole"},
                {"name": "eggs", "quantity": 2, "unit": "whole"},
                {"name": "lemon juice", "quantity": 1, "unit": "tsp"},
                {"name": "red pepper flakes", "quantity": 0.25, "unit": "tsp"},
                {"name": "salt", "quantity": 0.25, "unit": "tsp"},
                {"name": "black pepper", "quantity": 0.125, "unit": "tsp"},
            ],
            "instructions": {
                "steps": [
                    "Toast sourdough bread until golden and crispy",
                    "Mash avocado with lemon juice, salt, and pepper",
                    "Bring water to gentle simmer for poaching eggs",
                    "Crack eggs into simmering water and cook for 3-4 minutes",
                    "Spread avocado mixture on toast",
                    "Top with poached egg and red pepper flakes"
                ],
                "tips": ["Add white vinegar to poaching water for neater eggs"]
            },
            "nutritional_info": {
                "calories": 385,
                "protein_g": 16,
                "carbohydrates_g": 28,
                "fat_g": 24,
                "fiber_g": 9,
                "sugar_g": 3,
                "sodium_mg": 420,
                "cholesterol_mg": 186
            }
        },
        {
            "name": "Greek Yogurt Parfait",
            "description": "Layered parfait with Greek yogurt, granola, and fresh berries",
            "cuisine_type": "Greek",
            "difficulty": "easy",
            "prep_time": 10,
            "cook_time": 0,
            "servings": 2,
            "diet_types": ["vegetarian", "gluten-free"],
            "ingredients": [
                {"name": "Greek yogurt", "quantity": 2, "unit": "cups"},
                {"name": "honey", "quantity": 2, "unit": "tbsp"},
                {"name": "granola", "quantity": 0.5, "unit": "cup"},
                {"name": "fresh blueberries", "quantity": 0.5, "unit": "cup"},
                {"name": "fresh strawberries", "quantity": 0.5, "unit": "cup", "notes": "sliced"},
                {"name": "almonds", "quantity": 0.25, "unit": "cup", "notes": "sliced"},
            ],
            "instructions": {
                "steps": [
                    "Mix Greek yogurt with honey",
                    "Layer yogurt mixture in serving glasses",
                    "Add layer of granola",
                    "Top with mixed berries and almonds",
                    "Serve immediately or refrigerate up to 2 hours"
                ],
                "tips": ["Add granola just before serving to keep crunchy"]
            },
            "nutritional_info": {
                "calories": 340,
                "protein_g": 18,
                "carbohydrates_g": 45,
                "fat_g": 10,
                "fiber_g": 5,
                "sugar_g": 28,
                "sodium_mg": 85,
                "cholesterol_mg": 15
            }
        },
        {
            "name": "Fluffy Buttermilk Pancakes",
            "description": "Light and fluffy pancakes with buttermilk tang",
            "cuisine_type": "American",
            "difficulty": "easy",
            "prep_time": 10,
            "cook_time": 20,
            "servings": 4,
            "diet_types": ["vegetarian"],
            "ingredients": [
                {"name": "all-purpose flour", "quantity": 2, "unit": "cups"},
                {"name": "sugar", "quantity": 2, "unit": "tbsp"},
                {"name": "baking powder", "quantity": 2, "unit": "tsp"},
                {"name": "baking soda", "quantity": 0.5, "unit": "tsp"},
                {"name": "salt", "quantity": 0.5, "unit": "tsp"},
                {"name": "buttermilk", "quantity": 2, "unit": "cups"},
                {"name": "eggs", "quantity": 2, "unit": "whole"},
                {"name": "melted butter", "quantity": 0.25, "unit": "cup"},
            ],
            "instructions": {
                "steps": [
                    "Mix dry ingredients in large bowl",
                    "Whisk together buttermilk, eggs, and melted butter",
                    "Pour wet ingredients into dry, mix until just combined",
                    "Heat griddle to 375F",
                    "Pour 1/4 cup batter per pancake",
                    "Cook until bubbles form, flip and cook until golden"
                ],
                "tips": ["Don't overmix batter - lumps are okay", "Let batter rest 5 minutes before cooking"]
            },
            "nutritional_info": {
                "calories": 380,
                "protein_g": 11,
                "carbohydrates_g": 52,
                "fat_g": 14,
                "fiber_g": 2,
                "sugar_g": 12,
                "sodium_mg": 620,
                "cholesterol_mg": 125
            }
        },
        {
            "name": "Veggie Breakfast Burrito",
            "description": "Hearty breakfast burrito loaded with scrambled eggs and vegetables",
            "cuisine_type": "Mexican",
            "difficulty": "medium",
            "prep_time": 15,
            "cook_time": 15,
            "servings": 4,
            "diet_types": ["vegetarian"],
            "ingredients": [
                {"name": "large flour tortillas", "quantity": 4, "unit": "whole"},
                {"name": "eggs", "quantity": 8, "unit": "whole"},
                {"name": "bell peppers", "quantity": 1, "unit": "whole", "notes": "diced"},
                {"name": "onion", "quantity": 0.5, "unit": "whole", "notes": "diced"},
                {"name": "black beans", "quantity": 1, "unit": "cup", "notes": "drained"},
                {"name": "cheddar cheese", "quantity": 1, "unit": "cup", "notes": "shredded"},
                {"name": "salsa", "quantity": 0.5, "unit": "cup"},
                {"name": "sour cream", "quantity": 0.25, "unit": "cup"},
            ],
            "instructions": {
                "steps": [
                    "Sauté bell peppers and onions until soft",
                    "Scramble eggs in separate pan",
                    "Warm tortillas in microwave",
                    "Layer eggs, veggies, beans, and cheese on tortillas",
                    "Top with salsa and sour cream",
                    "Roll tightly and serve immediately"
                ],
                "tips": ["Can be wrapped in foil and frozen for meal prep"]
            },
            "nutritional_info": {
                "calories": 485,
                "protein_g": 26,
                "carbohydrates_g": 42,
                "fat_g": 22,
                "fiber_g": 6,
                "sugar_g": 5,
                "sodium_mg": 780,
                "cholesterol_mg": 395
            }
        },
        {
            "name": "Banana Oat Smoothie Bowl",
            "description": "Thick and creamy smoothie bowl topped with fresh fruit and nuts",
            "cuisine_type": "American",
            "difficulty": "easy",
            "prep_time": 10,
            "cook_time": 0,
            "servings": 2,
            "diet_types": ["vegan", "gluten-free"],
            "ingredients": [
                {"name": "frozen bananas", "quantity": 3, "unit": "whole"},
                {"name": "rolled oats", "quantity": 0.5, "unit": "cup"},
                {"name": "almond milk", "quantity": 0.5, "unit": "cup"},
                {"name": "peanut butter", "quantity": 2, "unit": "tbsp"},
                {"name": "chia seeds", "quantity": 1, "unit": "tbsp"},
                {"name": "fresh berries", "quantity": 0.5, "unit": "cup", "notes": "for topping"},
                {"name": "coconut flakes", "quantity": 2, "unit": "tbsp", "notes": "for topping"},
            ],
            "instructions": {
                "steps": [
                    "Blend frozen bananas, oats, almond milk, and peanut butter until smooth",
                    "Pour into bowls",
                    "Top with fresh berries, coconut flakes, and chia seeds",
                    "Serve immediately"
                ],
                "tips": ["Use very ripe bananas before freezing for best sweetness"]
            },
            "nutritional_info": {
                "calories": 380,
                "protein_g": 11,
                "carbohydrates_g": 62,
                "fat_g": 12,
                "fiber_g": 10,
                "sugar_g": 32,
                "sodium_mg": 95,
                "cholesterol_mg": 0
            }
        },
        {
            "name": "Spinach and Feta Omelet",
            "description": "Fluffy omelet filled with sautéed spinach and crumbled feta",
            "cuisine_type": "Mediterranean",
            "difficulty": "medium",
            "prep_time": 10,
            "cook_time": 10,
            "servings": 2,
            "diet_types": ["vegetarian", "gluten-free", "low-carb"],
            "ingredients": [
                {"name": "eggs", "quantity": 6, "unit": "whole"},
                {"name": "fresh spinach", "quantity": 2, "unit": "cups"},
                {"name": "feta cheese", "quantity": 0.5, "unit": "cup", "notes": "crumbled"},
                {"name": "butter", "quantity": 2, "unit": "tbsp"},
                {"name": "milk", "quantity": 2, "unit": "tbsp"},
                {"name": "salt", "quantity": 0.25, "unit": "tsp"},
                {"name": "black pepper", "quantity": 0.125, "unit": "tsp"},
            ],
            "instructions": {
                "steps": [
                    "Whisk eggs with milk, salt, and pepper",
                    "Sauté spinach until wilted, set aside",
                    "Melt butter in non-stick pan over medium heat",
                    "Pour egg mixture and cook until edges set",
                    "Add spinach and feta to one half",
                    "Fold omelet and cook 1 minute more",
                    "Slide onto plate and serve"
                ],
                "tips": ["Don't overcook - eggs should be slightly creamy"]
            },
            "nutritional_info": {
                "calories": 340,
                "protein_g": 24,
                "carbohydrates_g": 4,
                "fat_g": 26,
                "fiber_g": 1,
                "sugar_g": 2,
                "sodium_mg": 680,
                "cholesterol_mg": 575
            }
        }
    ]

    MAIN_COURSE_RECIPES = [
        {
            "name": "Spaghetti Carbonara",
            "description": "Classic Italian pasta with creamy egg sauce, pancetta, and pecorino",
            "cuisine_type": "Italian",
            "difficulty": "medium",
            "prep_time": 10,
            "cook_time": 20,
            "servings": 4,
            "diet_types": [],
            "ingredients": [
                {"name": "spaghetti", "quantity": 1, "unit": "lb"},
                {"name": "pancetta", "quantity": 6, "unit": "oz", "notes": "diced"},
                {"name": "egg yolks", "quantity": 4, "unit": "whole"},
                {"name": "whole eggs", "quantity": 2, "unit": "whole"},
                {"name": "pecorino romano", "quantity": 1, "unit": "cup", "notes": "grated"},
                {"name": "black pepper", "quantity": 1, "unit": "tsp", "notes": "freshly ground"},
                {"name": "salt", "quantity": 1, "unit": "tsp"},
            ],
            "instructions": {
                "steps": [
                    "Cook spaghetti in salted boiling water until al dente",
                    "Meanwhile, cook pancetta until crispy",
                    "Whisk together egg yolks, whole eggs, and pecorino",
                    "Reserve 1 cup pasta water, drain pasta",
                    "Remove pan from heat, add pasta to pancetta",
                    "Quickly stir in egg mixture with pasta water",
                    "Season with black pepper and serve immediately"
                ],
                "tips": ["Remove from heat before adding eggs to prevent scrambling", "Work quickly to create creamy sauce"]
            },
            "nutritional_info": {
                "calories": 620,
                "protein_g": 28,
                "carbohydrates_g": 68,
                "fat_g": 24,
                "fiber_g": 3,
                "sugar_g": 3,
                "sodium_mg": 850,
                "cholesterol_mg": 305
            }
        },
        {
            "name": "Grilled Chicken Teriyaki",
            "description": "Tender chicken breast glazed with homemade teriyaki sauce",
            "cuisine_type": "Japanese",
            "difficulty": "easy",
            "prep_time": 15,
            "cook_time": 20,
            "servings": 4,
            "diet_types": ["gluten-free"],
            "ingredients": [
                {"name": "chicken breasts", "quantity": 4, "unit": "whole"},
                {"name": "soy sauce", "quantity": 0.5, "unit": "cup"},
                {"name": "mirin", "quantity": 0.25, "unit": "cup"},
                {"name": "sake", "quantity": 0.25, "unit": "cup"},
                {"name": "sugar", "quantity": 2, "unit": "tbsp"},
                {"name": "fresh ginger", "quantity": 1, "unit": "tbsp", "notes": "grated"},
                {"name": "garlic", "quantity": 3, "unit": "cloves", "notes": "minced"},
                {"name": "sesame seeds", "quantity": 1, "unit": "tbsp", "notes": "for garnish"},
            ],
            "instructions": {
                "steps": [
                    "Combine soy sauce, mirin, sake, sugar, ginger, and garlic",
                    "Marinate chicken for at least 30 minutes",
                    "Preheat grill to medium-high heat",
                    "Grill chicken 6-7 minutes per side",
                    "Brush with teriyaki sauce while grilling",
                    "Let rest 5 minutes before slicing",
                    "Garnish with sesame seeds"
                ],
                "tips": ["Reserve some marinade for basting", "Don't overcook to keep chicken juicy"]
            },
            "nutritional_info": {
                "calories": 285,
                "protein_g": 38,
                "carbohydrates_g": 15,
                "fat_g": 6,
                "fiber_g": 0,
                "sugar_g": 11,
                "sodium_mg": 1850,
                "cholesterol_mg": 95
            }
        },
        {
            "name": "Vegetarian Chickpea Curry",
            "description": "Hearty Indian curry with chickpeas in spiced tomato sauce",
            "cuisine_type": "Indian",
            "difficulty": "medium",
            "prep_time": 15,
            "cook_time": 35,
            "servings": 6,
            "diet_types": ["vegetarian", "vegan", "gluten-free"],
            "ingredients": [
                {"name": "chickpeas", "quantity": 3, "unit": "cups", "notes": "cooked or canned"},
                {"name": "onions", "quantity": 2, "unit": "whole", "notes": "diced"},
                {"name": "tomatoes", "quantity": 4, "unit": "whole", "notes": "diced"},
                {"name": "coconut milk", "quantity": 1, "unit": "cup"},
                {"name": "curry powder", "quantity": 2, "unit": "tbsp"},
                {"name": "garam masala", "quantity": 1, "unit": "tsp"},
                {"name": "fresh ginger", "quantity": 1, "unit": "tbsp", "notes": "grated"},
                {"name": "garlic", "quantity": 4, "unit": "cloves", "notes": "minced"},
                {"name": "vegetable oil", "quantity": 2, "unit": "tbsp"},
            ],
            "instructions": {
                "steps": [
                    "Heat oil in large pot over medium heat",
                    "Sauté onions until golden, about 8 minutes",
                    "Add garlic and ginger, cook 1 minute",
                    "Stir in curry powder and garam masala",
                    "Add tomatoes and cook until broken down",
                    "Add chickpeas and coconut milk",
                    "Simmer 20 minutes until thickened",
                    "Serve over basmati rice with naan"
                ],
                "tips": ["Toast spices in dry pan first for deeper flavor", "Add spinach in last 5 minutes for extra nutrition"]
            },
            "nutritional_info": {
                "calories": 320,
                "protein_g": 12,
                "carbohydrates_g": 38,
                "fat_g": 14,
                "fiber_g": 10,
                "sugar_g": 8,
                "sodium_mg": 420,
                "cholesterol_mg": 0
            }
        },
        {
            "name": "Beef Tacos with Fresh Salsa",
            "description": "Seasoned ground beef tacos topped with homemade pico de gallo",
            "cuisine_type": "Mexican",
            "difficulty": "easy",
            "prep_time": 20,
            "cook_time": 15,
            "servings": 6,
            "diet_types": ["gluten-free"],
            "ingredients": [
                {"name": "ground beef", "quantity": 2, "unit": "lbs"},
                {"name": "taco seasoning", "quantity": 3, "unit": "tbsp"},
                {"name": "corn tortillas", "quantity": 12, "unit": "whole"},
                {"name": "tomatoes", "quantity": 4, "unit": "whole", "notes": "diced"},
                {"name": "onion", "quantity": 1, "unit": "whole", "notes": "diced"},
                {"name": "cilantro", "quantity": 0.5, "unit": "cup", "notes": "chopped"},
                {"name": "lime juice", "quantity": 2, "unit": "tbsp"},
                {"name": "cheddar cheese", "quantity": 2, "unit": "cups", "notes": "shredded"},
            ],
            "instructions": {
                "steps": [
                    "Brown ground beef in large skillet",
                    "Drain excess fat, add taco seasoning and water",
                    "Simmer until thickened",
                    "Mix tomatoes, onion, cilantro, and lime juice for salsa",
                    "Warm tortillas in dry skillet",
                    "Fill tortillas with beef, top with salsa and cheese",
                    "Serve with lime wedges"
                ],
                "tips": ["Char tortillas slightly for authentic flavor", "Make salsa ahead for flavors to meld"]
            },
            "nutritional_info": {
                "calories": 520,
                "protein_g": 36,
                "carbohydrates_g": 32,
                "fat_g": 26,
                "fiber_g": 5,
                "sugar_g": 4,
                "sodium_mg": 920,
                "cholesterol_mg": 110
            }
        },
        {
            "name": "Baked Salmon with Lemon Dill",
            "description": "Tender oven-baked salmon with fresh herbs and citrus",
            "cuisine_type": "Mediterranean",
            "difficulty": "easy",
            "prep_time": 10,
            "cook_time": 15,
            "servings": 4,
            "diet_types": ["gluten-free", "low-carb", "keto"],
            "ingredients": [
                {"name": "salmon fillets", "quantity": 4, "unit": "whole", "notes": "6 oz each"},
                {"name": "lemon", "quantity": 2, "unit": "whole", "notes": "sliced"},
                {"name": "fresh dill", "quantity": 0.25, "unit": "cup", "notes": "chopped"},
                {"name": "olive oil", "quantity": 2, "unit": "tbsp"},
                {"name": "garlic", "quantity": 3, "unit": "cloves", "notes": "minced"},
                {"name": "salt", "quantity": 1, "unit": "tsp"},
                {"name": "black pepper", "quantity": 0.5, "unit": "tsp"},
            ],
            "instructions": {
                "steps": [
                    "Preheat oven to 400F",
                    "Line baking sheet with parchment paper",
                    "Place salmon fillets skin-side down",
                    "Brush with olive oil and garlic",
                    "Season with salt, pepper, and dill",
                    "Top with lemon slices",
                    "Bake 12-15 minutes until flaky",
                    "Serve with roasted vegetables"
                ],
                "tips": ["Don't overcook - salmon should be slightly translucent in center", "Use a meat thermometer - 145F is perfect"]
            },
            "nutritional_info": {
                "calories": 340,
                "protein_g": 34,
                "carbohydrates_g": 2,
                "fat_g": 21,
                "fiber_g": 1,
                "sugar_g": 1,
                "sodium_mg": 650,
                "cholesterol_mg": 94
            }
        },
        {
            "name": "Mushroom Risotto",
            "description": "Creamy Italian rice dish with wild mushrooms and parmesan",
            "cuisine_type": "Italian",
            "difficulty": "hard",
            "prep_time": 15,
            "cook_time": 35,
            "servings": 4,
            "diet_types": ["vegetarian", "gluten-free"],
            "ingredients": [
                {"name": "arborio rice", "quantity": 1.5, "unit": "cups"},
                {"name": "mixed mushrooms", "quantity": 1, "unit": "lb", "notes": "sliced"},
                {"name": "vegetable broth", "quantity": 6, "unit": "cups", "notes": "warm"},
                {"name": "white wine", "quantity": 0.5, "unit": "cup"},
                {"name": "parmesan cheese", "quantity": 1, "unit": "cup", "notes": "grated"},
                {"name": "butter", "quantity": 4, "unit": "tbsp"},
                {"name": "shallots", "quantity": 2, "unit": "whole", "notes": "minced"},
                {"name": "fresh thyme", "quantity": 2, "unit": "tsp"},
            ],
            "instructions": {
                "steps": [
                    "Sauté mushrooms in 2 tbsp butter until golden",
                    "In separate pot, sauté shallots in remaining butter",
                    "Add rice, toast for 2 minutes",
                    "Add wine, stir until absorbed",
                    "Add broth one ladle at a time, stirring constantly",
                    "Continue until rice is creamy and al dente, about 25 minutes",
                    "Stir in mushrooms, parmesan, and thyme",
                    "Serve immediately"
                ],
                "tips": ["Keep broth warm throughout cooking", "Stir frequently but gently", "Rice should be creamy but grains distinct"]
            },
            "nutritional_info": {
                "calories": 445,
                "protein_g": 14,
                "carbohydrates_g": 58,
                "fat_g": 16,
                "fiber_g": 3,
                "sugar_g": 4,
                "sodium_mg": 980,
                "cholesterol_mg": 42
            }
        },
        {
            "name": "Thai Green Curry with Tofu",
            "description": "Aromatic Thai curry with vegetables and crispy tofu",
            "cuisine_type": "Thai",
            "difficulty": "medium",
            "prep_time": 20,
            "cook_time": 25,
            "servings": 4,
            "diet_types": ["vegan", "gluten-free"],
            "ingredients": [
                {"name": "firm tofu", "quantity": 14, "unit": "oz", "notes": "pressed and cubed"},
                {"name": "green curry paste", "quantity": 3, "unit": "tbsp"},
                {"name": "coconut milk", "quantity": 2, "unit": "cups"},
                {"name": "bamboo shoots", "quantity": 1, "unit": "cup"},
                {"name": "bell peppers", "quantity": 2, "unit": "whole", "notes": "sliced"},
                {"name": "Thai basil", "quantity": 0.5, "unit": "cup"},
                {"name": "fish sauce", "quantity": 2, "unit": "tbsp", "notes": "or soy sauce for vegan"},
                {"name": "palm sugar", "quantity": 1, "unit": "tbsp"},
            ],
            "instructions": {
                "steps": [
                    "Pan-fry tofu until golden and crispy",
                    "Heat curry paste in wok until fragrant",
                    "Add thick coconut cream, cook until oil separates",
                    "Add remaining coconut milk and vegetables",
                    "Simmer 15 minutes until vegetables tender",
                    "Add tofu, fish sauce, and sugar",
                    "Tear in Thai basil leaves",
                    "Serve over jasmine rice"
                ],
                "tips": ["Press tofu well for best texture", "Adjust curry paste amount to taste"]
            },
            "nutritional_info": {
                "calories": 380,
                "protein_g": 14,
                "carbohydrates_g": 22,
                "fat_g": 28,
                "fiber_g": 4,
                "sugar_g": 8,
                "sodium_mg": 1240,
                "cholesterol_mg": 0
            }
        },
        {
            "name": "Classic Beef Lasagna",
            "description": "Layered pasta with rich meat sauce, ricotta, and mozzarella",
            "cuisine_type": "Italian",
            "difficulty": "hard",
            "prep_time": 30,
            "cook_time": 60,
            "servings": 8,
            "diet_types": [],
            "ingredients": [
                {"name": "lasagna noodles", "quantity": 1, "unit": "lb"},
                {"name": "ground beef", "quantity": 1.5, "unit": "lbs"},
                {"name": "Italian sausage", "quantity": 0.5, "unit": "lb"},
                {"name": "marinara sauce", "quantity": 4, "unit": "cups"},
                {"name": "ricotta cheese", "quantity": 2, "unit": "cups"},
                {"name": "mozzarella cheese", "quantity": 4, "unit": "cups", "notes": "shredded"},
                {"name": "parmesan cheese", "quantity": 1, "unit": "cup", "notes": "grated"},
                {"name": "eggs", "quantity": 2, "unit": "whole"},
                {"name": "fresh basil", "quantity": 0.25, "unit": "cup", "notes": "chopped"},
            ],
            "instructions": {
                "steps": [
                    "Cook lasagna noodles according to package",
                    "Brown beef and sausage, drain fat",
                    "Stir in marinara sauce, simmer 20 minutes",
                    "Mix ricotta, eggs, half the mozzarella, basil",
                    "Spread sauce in 9x13 pan",
                    "Layer noodles, ricotta mixture, meat sauce, mozzarella",
                    "Repeat layers twice",
                    "Top with remaining mozzarella and parmesan",
                    "Bake at 375F for 45 minutes, let rest 15 minutes"
                ],
                "tips": ["Can assemble day ahead", "Cover with foil first 30 minutes to prevent over-browning"]
            },
            "nutritional_info": {
                "calories": 680,
                "protein_g": 42,
                "carbohydrates_g": 48,
                "fat_g": 34,
                "fiber_g": 4,
                "sugar_g": 10,
                "sodium_mg": 1380,
                "cholesterol_mg": 155
            }
        },
        {
            "name": "Lemon Herb Roasted Chicken",
            "description": "Whole roasted chicken with aromatic herbs and citrus",
            "cuisine_type": "American",
            "difficulty": "medium",
            "prep_time": 20,
            "cook_time": 90,
            "servings": 6,
            "diet_types": ["gluten-free", "low-carb"],
            "ingredients": [
                {"name": "whole chicken", "quantity": 1, "unit": "whole", "notes": "4-5 lbs"},
                {"name": "lemons", "quantity": 2, "unit": "whole"},
                {"name": "fresh rosemary", "quantity": 4, "unit": "sprigs"},
                {"name": "fresh thyme", "quantity": 6, "unit": "sprigs"},
                {"name": "garlic", "quantity": 1, "unit": "head", "notes": "halved"},
                {"name": "olive oil", "quantity": 3, "unit": "tbsp"},
                {"name": "butter", "quantity": 4, "unit": "tbsp", "notes": "softened"},
                {"name": "salt", "quantity": 2, "unit": "tsp"},
                {"name": "black pepper", "quantity": 1, "unit": "tsp"},
            ],
            "instructions": {
                "steps": [
                    "Preheat oven to 425F",
                    "Pat chicken dry, season inside and out",
                    "Stuff cavity with lemon halves, herbs, and garlic",
                    "Rub skin with butter and olive oil",
                    "Truss legs with kitchen twine",
                    "Roast 1 hour 20 minutes until 165F internal temp",
                    "Let rest 15 minutes before carving",
                    "Serve with pan juices"
                ],
                "tips": ["Use meat thermometer in thickest part of thigh", "Let chicken come to room temp before roasting"]
            },
            "nutritional_info": {
                "calories": 420,
                "protein_g": 38,
                "carbohydrates_g": 2,
                "fat_g": 28,
                "fiber_g": 0,
                "sugar_g": 1,
                "sodium_mg": 680,
                "cholesterol_mg": 135
            }
        },
        {
            "name": "Vegetarian Buddha Bowl",
            "description": "Nourishing bowl with quinoa, roasted vegetables, and tahini dressing",
            "cuisine_type": "American",
            "difficulty": "medium",
            "prep_time": 20,
            "cook_time": 30,
            "servings": 4,
            "diet_types": ["vegetarian", "vegan", "gluten-free"],
            "ingredients": [
                {"name": "quinoa", "quantity": 1.5, "unit": "cups"},
                {"name": "sweet potato", "quantity": 2, "unit": "whole", "notes": "cubed"},
                {"name": "chickpeas", "quantity": 2, "unit": "cups", "notes": "roasted"},
                {"name": "kale", "quantity": 4, "unit": "cups", "notes": "massaged"},
                {"name": "avocado", "quantity": 2, "unit": "whole", "notes": "sliced"},
                {"name": "tahini", "quantity": 0.25, "unit": "cup"},
                {"name": "lemon juice", "quantity": 3, "unit": "tbsp"},
                {"name": "maple syrup", "quantity": 1, "unit": "tbsp"},
            ],
            "instructions": {
                "steps": [
                    "Cook quinoa according to package directions",
                    "Toss sweet potato with oil, roast at 425F for 25 minutes",
                    "Roast chickpeas until crispy",
                    "Massage kale with lemon juice",
                    "Whisk together tahini, lemon juice, maple syrup, water",
                    "Arrange quinoa, vegetables, and chickpeas in bowls",
                    "Top with avocado and drizzle with dressing"
                ],
                "tips": ["Prep components ahead for easy assembly", "Customize with your favorite vegetables"]
            },
            "nutritional_info": {
                "calories": 520,
                "protein_g": 18,
                "carbohydrates_g": 68,
                "fat_g": 20,
                "fiber_g": 14,
                "sugar_g": 10,
                "sodium_mg": 340,
                "cholesterol_mg": 0
            }
        },
        {
            "name": "Shrimp Pad Thai",
            "description": "Classic Thai stir-fried noodles with shrimp, peanuts, and lime",
            "cuisine_type": "Thai",
            "difficulty": "medium",
            "prep_time": 25,
            "cook_time": 15,
            "servings": 4,
            "diet_types": ["gluten-free"],
            "ingredients": [
                {"name": "rice noodles", "quantity": 8, "unit": "oz"},
                {"name": "shrimp", "quantity": 1, "unit": "lb", "notes": "peeled and deveined"},
                {"name": "eggs", "quantity": 3, "unit": "whole"},
                {"name": "bean sprouts", "quantity": 2, "unit": "cups"},
                {"name": "scallions", "quantity": 4, "unit": "whole", "notes": "chopped"},
                {"name": "peanuts", "quantity": 0.5, "unit": "cup", "notes": "crushed"},
                {"name": "tamarind paste", "quantity": 3, "unit": "tbsp"},
                {"name": "fish sauce", "quantity": 3, "unit": "tbsp"},
                {"name": "palm sugar", "quantity": 2, "unit": "tbsp"},
                {"name": "lime", "quantity": 2, "unit": "whole", "notes": "cut into wedges"},
            ],
            "instructions": {
                "steps": [
                    "Soak rice noodles in warm water 30 minutes",
                    "Mix tamarind paste, fish sauce, and sugar for sauce",
                    "Heat wok over high heat",
                    "Stir-fry shrimp until pink, remove",
                    "Scramble eggs, add drained noodles and sauce",
                    "Toss until noodles absorb sauce",
                    "Add shrimp, bean sprouts, scallions",
                    "Serve with peanuts and lime wedges"
                ],
                "tips": ["Have all ingredients prepped before starting", "Work fast over high heat", "Don't over-soak noodles"]
            },
            "nutritional_info": {
                "calories": 485,
                "protein_g": 32,
                "carbohydrates_g": 58,
                "fat_g": 14,
                "fiber_g": 4,
                "sugar_g": 12,
                "sodium_mg": 1650,
                "cholesterol_mg": 265
            }
        },
        {
            "name": "Eggplant Parmesan",
            "description": "Breaded eggplant slices baked with marinara and mozzarella",
            "cuisine_type": "Italian",
            "difficulty": "medium",
            "prep_time": 30,
            "cook_time": 40,
            "servings": 6,
            "diet_types": ["vegetarian"],
            "ingredients": [
                {"name": "eggplants", "quantity": 2, "unit": "whole", "notes": "sliced 1/4 inch"},
                {"name": "marinara sauce", "quantity": 3, "unit": "cups"},
                {"name": "mozzarella cheese", "quantity": 3, "unit": "cups", "notes": "shredded"},
                {"name": "parmesan cheese", "quantity": 1, "unit": "cup", "notes": "grated"},
                {"name": "breadcrumbs", "quantity": 2, "unit": "cups"},
                {"name": "eggs", "quantity": 3, "unit": "whole"},
                {"name": "flour", "quantity": 1, "unit": "cup"},
                {"name": "fresh basil", "quantity": 0.25, "unit": "cup", "notes": "chopped"},
            ],
            "instructions": {
                "steps": [
                    "Salt eggplant slices, let drain 30 minutes",
                    "Set up breading station: flour, beaten eggs, breadcrumbs",
                    "Bread eggplant slices and bake at 400F until golden",
                    "Layer sauce, eggplant, mozzarella in baking dish",
                    "Repeat layers, top with parmesan",
                    "Bake at 375F for 30 minutes until bubbly",
                    "Let rest 10 minutes, garnish with basil"
                ],
                "tips": ["Salting removes bitterness and excess moisture", "Can be assembled ahead and frozen"]
            },
            "nutritional_info": {
                "calories": 445,
                "protein_g": 24,
                "carbohydrates_g": 42,
                "fat_g": 20,
                "fiber_g": 8,
                "sugar_g": 12,
                "sodium_mg": 1120,
                "cholesterol_mg": 135
            }
        },
        {
            "name": "Korean Bibimbap",
            "description": "Mixed rice bowl with seasoned vegetables, beef, and gochujang",
            "cuisine_type": "Korean",
            "difficulty": "hard",
            "prep_time": 40,
            "cook_time": 20,
            "servings": 4,
            "diet_types": [],
            "ingredients": [
                {"name": "short grain rice", "quantity": 3, "unit": "cups", "notes": "cooked"},
                {"name": "beef sirloin", "quantity": 8, "unit": "oz", "notes": "thinly sliced"},
                {"name": "spinach", "quantity": 2, "unit": "cups"},
                {"name": "bean sprouts", "quantity": 2, "unit": "cups"},
                {"name": "carrots", "quantity": 2, "unit": "whole", "notes": "julienned"},
                {"name": "mushrooms", "quantity": 4, "unit": "oz", "notes": "sliced"},
                {"name": "eggs", "quantity": 4, "unit": "whole"},
                {"name": "gochujang", "quantity": 4, "unit": "tbsp"},
                {"name": "sesame oil", "quantity": 2, "unit": "tbsp"},
                {"name": "soy sauce", "quantity": 3, "unit": "tbsp"},
            ],
            "instructions": {
                "steps": [
                    "Marinate beef in soy sauce and sesame oil",
                    "Blanch spinach and bean sprouts separately",
                    "Sauté carrots and mushrooms until tender",
                    "Stir-fry beef until cooked",
                    "Fry eggs sunny-side up",
                    "Divide rice into bowls",
                    "Arrange vegetables and beef on top",
                    "Top with fried egg and dollop of gochujang",
                    "Mix everything together before eating"
                ],
                "tips": ["Keep each vegetable separate for visual appeal", "Use stone bowl for authentic crispy rice bottom"]
            },
            "nutritional_info": {
                "calories": 580,
                "protein_g": 28,
                "carbohydrates_g": 72,
                "fat_g": 18,
                "fiber_g": 6,
                "sugar_g": 8,
                "sodium_mg": 1240,
                "cholesterol_mg": 220
            }
        },
        {
            "name": "Moroccan Lamb Tagine",
            "description": "Slow-cooked lamb with apricots, almonds, and warm spices",
            "cuisine_type": "Moroccan",
            "difficulty": "hard",
            "prep_time": 25,
            "cook_time": 120,
            "servings": 6,
            "diet_types": ["gluten-free"],
            "ingredients": [
                {"name": "lamb shoulder", "quantity": 2.5, "unit": "lbs", "notes": "cubed"},
                {"name": "dried apricots", "quantity": 1, "unit": "cup"},
                {"name": "almonds", "quantity": 0.5, "unit": "cup", "notes": "toasted"},
                {"name": "onions", "quantity": 2, "unit": "whole", "notes": "sliced"},
                {"name": "tomatoes", "quantity": 3, "unit": "whole", "notes": "diced"},
                {"name": "chickpeas", "quantity": 1.5, "unit": "cups", "notes": "cooked"},
                {"name": "ras el hanout", "quantity": 2, "unit": "tbsp"},
                {"name": "honey", "quantity": 2, "unit": "tbsp"},
                {"name": "lamb stock", "quantity": 3, "unit": "cups"},
            ],
            "instructions": {
                "steps": [
                    "Brown lamb in batches in Dutch oven",
                    "Sauté onions until soft",
                    "Add ras el hanout, toast 1 minute",
                    "Return lamb, add tomatoes and stock",
                    "Bring to boil, cover, simmer 90 minutes",
                    "Add apricots, chickpeas, honey",
                    "Cook 30 minutes more until lamb tender",
                    "Garnish with toasted almonds",
                    "Serve over couscous"
                ],
                "tips": ["Can also cook in slow cooker on low 6-8 hours", "Lamb should be fall-apart tender"]
            },
            "nutritional_info": {
                "calories": 520,
                "protein_g": 38,
                "carbohydrates_g": 42,
                "fat_g": 22,
                "fiber_g": 8,
                "sugar_g": 22,
                "sodium_mg": 480,
                "cholesterol_mg": 105
            }
        },
        {
            "name": "Fish and Chips",
            "description": "Beer-battered cod with crispy fries and tartar sauce",
            "cuisine_type": "British",
            "difficulty": "hard",
            "prep_time": 30,
            "cook_time": 30,
            "servings": 4,
            "diet_types": [],
            "ingredients": [
                {"name": "cod fillets", "quantity": 1.5, "unit": "lbs"},
                {"name": "russet potatoes", "quantity": 4, "unit": "whole"},
                {"name": "all-purpose flour", "quantity": 2, "unit": "cups"},
                {"name": "beer", "quantity": 1.5, "unit": "cups"},
                {"name": "baking powder", "quantity": 2, "unit": "tsp"},
                {"name": "vegetable oil", "quantity": 8, "unit": "cups", "notes": "for frying"},
                {"name": "malt vinegar", "quantity": 0.25, "unit": "cup"},
                {"name": "mayonnaise", "quantity": 0.5, "unit": "cup", "notes": "for tartar sauce"},
                {"name": "pickles", "quantity": 0.25, "unit": "cup", "notes": "minced, for tartar sauce"},
            ],
            "instructions": {
                "steps": [
                    "Cut potatoes into fries, soak in cold water",
                    "Mix flour, baking powder, salt, and beer for batter",
                    "Heat oil to 350F",
                    "Dry potatoes, fry until golden, about 5 minutes",
                    "Increase oil temp to 375F",
                    "Dip fish in batter, fry 5-6 minutes until golden",
                    "Double-fry potatoes at 375F for extra crisp",
                    "Mix mayo and pickles for tartar sauce",
                    "Serve with malt vinegar"
                ],
                "tips": ["Keep fried items warm in 200F oven", "Don't overcrowd fryer", "Use candy thermometer for oil temp"]
            },
            "nutritional_info": {
                "calories": 780,
                "protein_g": 38,
                "carbohydrates_g": 82,
                "fat_g": 34,
                "fiber_g": 6,
                "sugar_g": 4,
                "sodium_mg": 680,
                "cholesterol_mg": 85
            }
        }
    ]

    APPETIZER_RECIPES = [
        {
            "name": "Bruschetta with Tomato Basil",
            "description": "Toasted bread topped with fresh tomatoes, basil, and garlic",
            "cuisine_type": "Italian",
            "difficulty": "easy",
            "prep_time": 15,
            "cook_time": 5,
            "servings": 8,
            "diet_types": ["vegetarian", "vegan"],
            "ingredients": [
                {"name": "baguette", "quantity": 1, "unit": "whole", "notes": "sliced"},
                {"name": "tomatoes", "quantity": 4, "unit": "whole", "notes": "diced"},
                {"name": "fresh basil", "quantity": 0.5, "unit": "cup", "notes": "chopped"},
                {"name": "garlic", "quantity": 3, "unit": "cloves", "notes": "minced"},
                {"name": "olive oil", "quantity": 0.25, "unit": "cup"},
                {"name": "balsamic vinegar", "quantity": 1, "unit": "tbsp"},
                {"name": "salt", "quantity": 0.5, "unit": "tsp"},
            ],
            "instructions": {
                "steps": [
                    "Toast baguette slices until golden",
                    "Mix tomatoes, basil, garlic, oil, vinegar, salt",
                    "Let mixture sit 10 minutes for flavors to meld",
                    "Rub toasted bread with garlic clove",
                    "Top with tomato mixture just before serving"
                ],
                "tips": ["Don't top bread too early or it will get soggy"]
            },
            "nutritional_info": {
                "calories": 145,
                "protein_g": 4,
                "carbohydrates_g": 20,
                "fat_g": 6,
                "fiber_g": 2,
                "sugar_g": 3,
                "sodium_mg": 240,
                "cholesterol_mg": 0
            }
        },
        {
            "name": "Buffalo Chicken Wings",
            "description": "Crispy fried wings tossed in spicy buffalo sauce",
            "cuisine_type": "American",
            "difficulty": "medium",
            "prep_time": 15,
            "cook_time": 25,
            "servings": 6,
            "diet_types": ["gluten-free"],
            "ingredients": [
                {"name": "chicken wings", "quantity": 3, "unit": "lbs"},
                {"name": "hot sauce", "quantity": 0.5, "unit": "cup"},
                {"name": "butter", "quantity": 4, "unit": "tbsp", "notes": "melted"},
                {"name": "garlic powder", "quantity": 1, "unit": "tsp"},
                {"name": "salt", "quantity": 1, "unit": "tsp"},
                {"name": "vegetable oil", "quantity": 4, "unit": "cups", "notes": "for frying"},
                {"name": "blue cheese dressing", "quantity": 1, "unit": "cup", "notes": "for serving"},
            ],
            "instructions": {
                "steps": [
                    "Pat wings dry, season with salt and garlic powder",
                    "Heat oil to 375F",
                    "Fry wings in batches 10-12 minutes until crispy",
                    "Mix hot sauce and melted butter",
                    "Toss fried wings in buffalo sauce",
                    "Serve with blue cheese dressing and celery"
                ],
                "tips": ["Bake at 425F for healthier version", "Double fry for extra crispy wings"]
            },
            "nutritional_info": {
                "calories": 420,
                "protein_g": 26,
                "carbohydrates_g": 2,
                "fat_g": 34,
                "fiber_g": 0,
                "sugar_g": 1,
                "sodium_mg": 1820,
                "cholesterol_mg": 115
            }
        },
        {
            "name": "Spinach Artichoke Dip",
            "description": "Creamy baked dip with spinach, artichokes, and cheese",
            "cuisine_type": "American",
            "difficulty": "easy",
            "prep_time": 15,
            "cook_time": 25,
            "servings": 8,
            "diet_types": ["vegetarian", "gluten-free"],
            "ingredients": [
                {"name": "frozen spinach", "quantity": 10, "unit": "oz", "notes": "thawed and drained"},
                {"name": "artichoke hearts", "quantity": 1, "unit": "cup", "notes": "chopped"},
                {"name": "cream cheese", "quantity": 8, "unit": "oz", "notes": "softened"},
                {"name": "sour cream", "quantity": 0.5, "unit": "cup"},
                {"name": "mayonnaise", "quantity": 0.25, "unit": "cup"},
                {"name": "parmesan cheese", "quantity": 0.5, "unit": "cup", "notes": "grated"},
                {"name": "mozzarella cheese", "quantity": 1, "unit": "cup", "notes": "shredded"},
                {"name": "garlic", "quantity": 3, "unit": "cloves", "notes": "minced"},
            ],
            "instructions": {
                "steps": [
                    "Preheat oven to 375F",
                    "Mix all ingredients except half the mozzarella",
                    "Spread in baking dish",
                    "Top with remaining mozzarella",
                    "Bake 25 minutes until bubbly and golden",
                    "Serve warm with tortilla chips or bread"
                ],
                "tips": ["Squeeze spinach very dry", "Can make in slow cooker on low 2 hours"]
            },
            "nutritional_info": {
                "calories": 245,
                "protein_g": 10,
                "carbohydrates_g": 8,
                "fat_g": 20,
                "fiber_g": 2,
                "sugar_g": 2,
                "sodium_mg": 520,
                "cholesterol_mg": 55
            }
        },
        {
            "name": "Crispy Spring Rolls",
            "description": "Vietnamese rice paper rolls with vegetables and shrimp",
            "cuisine_type": "Vietnamese",
            "difficulty": "medium",
            "prep_time": 30,
            "cook_time": 0,
            "servings": 8,
            "diet_types": ["gluten-free"],
            "ingredients": [
                {"name": "rice paper wrappers", "quantity": 16, "unit": "sheets"},
                {"name": "cooked shrimp", "quantity": 1, "unit": "lb", "notes": "halved"},
                {"name": "rice vermicelli", "quantity": 4, "unit": "oz", "notes": "cooked"},
                {"name": "lettuce", "quantity": 2, "unit": "cups", "notes": "shredded"},
                {"name": "carrots", "quantity": 1, "unit": "whole", "notes": "julienned"},
                {"name": "cucumber", "quantity": 1, "unit": "whole", "notes": "julienned"},
                {"name": "fresh mint", "quantity": 0.5, "unit": "cup"},
                {"name": "peanut sauce", "quantity": 1, "unit": "cup", "notes": "for dipping"},
            ],
            "instructions": {
                "steps": [
                    "Soak rice paper in warm water 10 seconds",
                    "Lay on damp towel",
                    "Place filling in center: lettuce, noodles, shrimp, vegetables, mint",
                    "Fold sides in, roll tightly",
                    "Keep under damp towel until serving",
                    "Serve with peanut sauce"
                ],
                "tips": ["Don't oversoak rice paper", "Work with one wrapper at a time"]
            },
            "nutritional_info": {
                "calories": 180,
                "protein_g": 14,
                "carbohydrates_g": 24,
                "fat_g": 3,
                "fiber_g": 2,
                "sugar_g": 4,
                "sodium_mg": 320,
                "cholesterol_mg": 95
            }
        },
        {
            "name": "Stuffed Mushrooms",
            "description": "Button mushrooms filled with herb breadcrumb mixture",
            "cuisine_type": "Italian",
            "difficulty": "easy",
            "prep_time": 20,
            "cook_time": 25,
            "servings": 6,
            "diet_types": ["vegetarian"],
            "ingredients": [
                {"name": "large mushrooms", "quantity": 24, "unit": "whole", "notes": "stems removed"},
                {"name": "breadcrumbs", "quantity": 1, "unit": "cup"},
                {"name": "parmesan cheese", "quantity": 0.5, "unit": "cup", "notes": "grated"},
                {"name": "cream cheese", "quantity": 4, "unit": "oz", "notes": "softened"},
                {"name": "garlic", "quantity": 3, "unit": "cloves", "notes": "minced"},
                {"name": "fresh parsley", "quantity": 0.25, "unit": "cup", "notes": "chopped"},
                {"name": "olive oil", "quantity": 2, "unit": "tbsp"},
            ],
            "instructions": {
                "steps": [
                    "Preheat oven to 375F",
                    "Chop mushroom stems finely",
                    "Sauté stems and garlic in olive oil",
                    "Mix with breadcrumbs, parmesan, cream cheese, parsley",
                    "Fill mushroom caps with mixture",
                    "Bake 20-25 minutes until golden",
                    "Serve warm"
                ],
                "tips": ["Can prep ahead and refrigerate before baking"]
            },
            "nutritional_info": {
                "calories": 165,
                "protein_g": 8,
                "carbohydrates_g": 14,
                "fat_g": 9,
                "fiber_g": 2,
                "sugar_g": 3,
                "sodium_mg": 280,
                "cholesterol_mg": 22
            }
        },
        {
            "name": "Caprese Skewers",
            "description": "Cherry tomatoes, mozzarella, and basil on skewers",
            "cuisine_type": "Italian",
            "difficulty": "easy",
            "prep_time": 15,
            "cook_time": 0,
            "servings": 12,
            "diet_types": ["vegetarian", "gluten-free", "low-carb"],
            "ingredients": [
                {"name": "cherry tomatoes", "quantity": 24, "unit": "whole"},
                {"name": "mozzarella balls", "quantity": 24, "unit": "whole"},
                {"name": "fresh basil leaves", "quantity": 24, "unit": "leaves"},
                {"name": "balsamic glaze", "quantity": 0.25, "unit": "cup"},
                {"name": "olive oil", "quantity": 2, "unit": "tbsp"},
                {"name": "salt", "quantity": 0.25, "unit": "tsp"},
                {"name": "black pepper", "quantity": 0.125, "unit": "tsp"},
            ],
            "instructions": {
                "steps": [
                    "Thread tomato, basil leaf, and mozzarella on skewers",
                    "Arrange on serving platter",
                    "Drizzle with olive oil and balsamic glaze",
                    "Season with salt and pepper",
                    "Serve at room temperature"
                ],
                "tips": ["Make just before serving for best presentation"]
            },
            "nutritional_info": {
                "calories": 95,
                "protein_g": 6,
                "carbohydrates_g": 4,
                "fat_g": 6,
                "fiber_g": 1,
                "sugar_g": 3,
                "sodium_mg": 180,
                "cholesterol_mg": 18
            }
        },
        {
            "name": "Guacamole and Chips",
            "description": "Fresh avocado dip with lime and cilantro",
            "cuisine_type": "Mexican",
            "difficulty": "easy",
            "prep_time": 10,
            "cook_time": 0,
            "servings": 6,
            "diet_types": ["vegan", "gluten-free"],
            "ingredients": [
                {"name": "ripe avocados", "quantity": 4, "unit": "whole"},
                {"name": "lime juice", "quantity": 3, "unit": "tbsp"},
                {"name": "red onion", "quantity": 0.25, "unit": "cup", "notes": "minced"},
                {"name": "jalapeño", "quantity": 1, "unit": "whole", "notes": "minced"},
                {"name": "fresh cilantro", "quantity": 0.25, "unit": "cup", "notes": "chopped"},
                {"name": "tomato", "quantity": 1, "unit": "whole", "notes": "diced"},
                {"name": "salt", "quantity": 0.5, "unit": "tsp"},
                {"name": "tortilla chips", "quantity": 8, "unit": "oz", "notes": "for serving"},
            ],
            "instructions": {
                "steps": [
                    "Mash avocados in bowl with fork",
                    "Mix in lime juice, onion, jalapeño, cilantro",
                    "Fold in diced tomato",
                    "Season with salt to taste",
                    "Serve immediately with tortilla chips"
                ],
                "tips": ["Press plastic wrap directly on surface to prevent browning", "Leave avocado pit in dip to keep green longer"]
            },
            "nutritional_info": {
                "calories": 245,
                "protein_g": 3,
                "carbohydrates_g": 22,
                "fat_g": 18,
                "fiber_g": 8,
                "sugar_g": 2,
                "sodium_mg": 320,
                "cholesterol_mg": 0
            }
        }
    ]

    DESSERT_RECIPES = [
        {
            "name": "Classic Tiramisu",
            "description": "Italian coffee-flavored dessert with mascarpone and ladyfingers",
            "cuisine_type": "Italian",
            "difficulty": "medium",
            "prep_time": 30,
            "cook_time": 0,
            "servings": 12,
            "diet_types": ["vegetarian"],
            "ingredients": [
                {"name": "ladyfinger cookies", "quantity": 24, "unit": "whole"},
                {"name": "espresso", "quantity": 1.5, "unit": "cups", "notes": "cooled"},
                {"name": "mascarpone cheese", "quantity": 16, "unit": "oz"},
                {"name": "egg yolks", "quantity": 6, "unit": "whole"},
                {"name": "sugar", "quantity": 0.75, "unit": "cup"},
                {"name": "heavy cream", "quantity": 1.5, "unit": "cups"},
                {"name": "cocoa powder", "quantity": 0.25, "unit": "cup"},
                {"name": "vanilla extract", "quantity": 1, "unit": "tsp"},
            ],
            "instructions": {
                "steps": [
                    "Whisk egg yolks and sugar until thick and pale",
                    "Beat in mascarpone until smooth",
                    "Whip cream to stiff peaks, fold into mascarpone",
                    "Quickly dip ladyfingers in espresso",
                    "Layer in dish: ladyfingers, mascarpone cream",
                    "Repeat layers",
                    "Dust with cocoa powder",
                    "Refrigerate at least 4 hours or overnight"
                ],
                "tips": ["Don't oversoak ladyfingers", "Best made day ahead"]
            },
            "nutritional_info": {
                "calories": 385,
                "protein_g": 7,
                "carbohydrates_g": 32,
                "fat_g": 26,
                "fiber_g": 1,
                "sugar_g": 22,
                "sodium_mg": 95,
                "cholesterol_mg": 195
            }
        },
        {
            "name": "New York Cheesecake",
            "description": "Rich and creamy cheesecake with graham cracker crust",
            "cuisine_type": "American",
            "difficulty": "hard",
            "prep_time": 30,
            "cook_time": 90,
            "servings": 12,
            "diet_types": ["vegetarian"],
            "ingredients": [
                {"name": "graham crackers", "quantity": 2, "unit": "cups", "notes": "crushed"},
                {"name": "butter", "quantity": 0.5, "unit": "cup", "notes": "melted"},
                {"name": "cream cheese", "quantity": 32, "unit": "oz", "notes": "softened"},
                {"name": "sugar", "quantity": 1.25, "unit": "cups"},
                {"name": "eggs", "quantity": 4, "unit": "whole"},
                {"name": "sour cream", "quantity": 1, "unit": "cup"},
                {"name": "vanilla extract", "quantity": 2, "unit": "tsp"},
                {"name": "lemon zest", "quantity": 1, "unit": "tbsp"},
            ],
            "instructions": {
                "steps": [
                    "Mix graham cracker crumbs and melted butter",
                    "Press into 9-inch springform pan",
                    "Beat cream cheese and sugar until fluffy",
                    "Add eggs one at a time",
                    "Mix in sour cream, vanilla, and lemon zest",
                    "Pour over crust",
                    "Bake at 325F for 70 minutes",
                    "Turn off oven, leave door cracked 1 hour",
                    "Chill overnight before serving"
                ],
                "tips": ["Use water bath to prevent cracks", "All ingredients should be room temperature"]
            },
            "nutritional_info": {
                "calories": 485,
                "protein_g": 8,
                "carbohydrates_g": 42,
                "fat_g": 32,
                "fiber_g": 1,
                "sugar_g": 32,
                "sodium_mg": 380,
                "cholesterol_mg": 155
            }
        },
        {
            "name": "Chocolate Lava Cake",
            "description": "Individual molten chocolate cakes with gooey centers",
            "cuisine_type": "French",
            "difficulty": "medium",
            "prep_time": 15,
            "cook_time": 12,
            "servings": 4,
            "diet_types": ["vegetarian"],
            "ingredients": [
                {"name": "dark chocolate", "quantity": 6, "unit": "oz", "notes": "chopped"},
                {"name": "butter", "quantity": 6, "unit": "tbsp"},
                {"name": "eggs", "quantity": 2, "unit": "whole"},
                {"name": "egg yolks", "quantity": 2, "unit": "whole"},
                {"name": "sugar", "quantity": 0.25, "unit": "cup"},
                {"name": "flour", "quantity": 2, "unit": "tbsp"},
                {"name": "vanilla extract", "quantity": 0.5, "unit": "tsp"},
                {"name": "powdered sugar", "quantity": 2, "unit": "tbsp", "notes": "for dusting"},
            ],
            "instructions": {
                "steps": [
                    "Butter and flour 4 ramekins",
                    "Melt chocolate and butter together",
                    "Whisk eggs, yolks, and sugar until thick",
                    "Fold in chocolate mixture",
                    "Gently fold in flour and vanilla",
                    "Divide among ramekins",
                    "Bake at 450F for 12-14 minutes",
                    "Centers should be soft",
                    "Invert onto plates, dust with powdered sugar",
                    "Serve immediately"
                ],
                "tips": ["Can prep ahead and refrigerate, add 2 minutes to bake time", "Timing is crucial - watch carefully"]
            },
            "nutritional_info": {
                "calories": 445,
                "protein_g": 8,
                "carbohydrates_g": 38,
                "fat_g": 30,
                "fiber_g": 3,
                "sugar_g": 28,
                "sodium_mg": 135,
                "cholesterol_mg": 245
            }
        },
        {
            "name": "Apple Pie",
            "description": "Classic double-crust pie with spiced apple filling",
            "cuisine_type": "American",
            "difficulty": "hard",
            "prep_time": 45,
            "cook_time": 55,
            "servings": 8,
            "diet_types": ["vegetarian"],
            "ingredients": [
                {"name": "pie dough", "quantity": 2, "unit": "discs", "notes": "for double crust"},
                {"name": "granny smith apples", "quantity": 6, "unit": "whole", "notes": "sliced"},
                {"name": "sugar", "quantity": 0.75, "unit": "cup"},
                {"name": "flour", "quantity": 2, "unit": "tbsp"},
                {"name": "cinnamon", "quantity": 1, "unit": "tsp"},
                {"name": "nutmeg", "quantity": 0.25, "unit": "tsp"},
                {"name": "lemon juice", "quantity": 1, "unit": "tbsp"},
                {"name": "butter", "quantity": 2, "unit": "tbsp"},
            ],
            "instructions": {
                "steps": [
                    "Roll out bottom crust, fit into 9-inch pie pan",
                    "Mix apples with sugar, flour, cinnamon, nutmeg, lemon juice",
                    "Pour filling into crust",
                    "Dot with butter",
                    "Cover with top crust, crimp edges",
                    "Cut vents in top",
                    "Brush with egg wash, sprinkle with sugar",
                    "Bake at 375F for 55 minutes until golden",
                    "Cool completely before slicing"
                ],
                "tips": ["Use variety of apples for best flavor", "Shield edges with foil if browning too fast"]
            },
            "nutritional_info": {
                "calories": 420,
                "protein_g": 4,
                "carbohydrates_g": 68,
                "fat_g": 16,
                "fiber_g": 4,
                "sugar_g": 38,
                "sodium_mg": 280,
                "cholesterol_mg": 35
            }
        },
        {
            "name": "Crème Brûlée",
            "description": "French custard dessert with caramelized sugar topping",
            "cuisine_type": "French",
            "difficulty": "hard",
            "prep_time": 20,
            "cook_time": 45,
            "servings": 6,
            "diet_types": ["vegetarian", "gluten-free"],
            "ingredients": [
                {"name": "heavy cream", "quantity": 2, "unit": "cups"},
                {"name": "egg yolks", "quantity": 6, "unit": "whole"},
                {"name": "sugar", "quantity": 0.5, "unit": "cup"},
                {"name": "vanilla bean", "quantity": 1, "unit": "whole", "notes": "split"},
                {"name": "superfine sugar", "quantity": 6, "unit": "tbsp", "notes": "for topping"},
            ],
            "instructions": {
                "steps": [
                    "Heat cream with vanilla bean to simmer",
                    "Whisk yolks and sugar until pale",
                    "Slowly whisk hot cream into yolks",
                    "Strain through fine sieve",
                    "Pour into 6 ramekins",
                    "Place in water bath",
                    "Bake at 325F for 40-45 minutes until just set",
                    "Chill at least 4 hours",
                    "Sprinkle sugar on top, torch until caramelized",
                    "Serve immediately after caramelizing"
                ],
                "tips": ["Custard should jiggle slightly when done", "Use torch for best caramelization"]
            },
            "nutritional_info": {
                "calories": 365,
                "protein_g": 5,
                "carbohydrates_g": 28,
                "fat_g": 27,
                "fiber_g": 0,
                "sugar_g": 26,
                "sodium_mg": 45,
                "cholesterol_mg": 325
            }
        },
        {
            "name": "Lemon Bars",
            "description": "Tangy lemon custard on buttery shortbread crust",
            "cuisine_type": "American",
            "difficulty": "medium",
            "prep_time": 20,
            "cook_time": 50,
            "servings": 16,
            "diet_types": ["vegetarian"],
            "ingredients": [
                {"name": "flour", "quantity": 2, "unit": "cups"},
                {"name": "butter", "quantity": 1, "unit": "cup", "notes": "softened"},
                {"name": "powdered sugar", "quantity": 0.5, "unit": "cup"},
                {"name": "eggs", "quantity": 4, "unit": "whole"},
                {"name": "sugar", "quantity": 2, "unit": "cups"},
                {"name": "lemon juice", "quantity": 0.5, "unit": "cup"},
                {"name": "lemon zest", "quantity": 2, "unit": "tbsp"},
                {"name": "baking powder", "quantity": 0.25, "unit": "tsp"},
            ],
            "instructions": {
                "steps": [
                    "Mix 1.5 cups flour, butter, and powdered sugar",
                    "Press into 9x13 pan",
                    "Bake at 350F for 20 minutes",
                    "Whisk eggs, sugar, remaining flour, baking powder",
                    "Stir in lemon juice and zest",
                    "Pour over hot crust",
                    "Bake 25 minutes more until set",
                    "Cool completely, dust with powdered sugar",
                    "Cut into squares"
                ],
                "tips": ["Pour filling over hot crust for best adhesion", "Chill before cutting for clean edges"]
            },
            "nutritional_info": {
                "calories": 285,
                "protein_g": 3,
                "carbohydrates_g": 42,
                "fat_g": 12,
                "fiber_g": 1,
                "sugar_g": 30,
                "sodium_mg": 95,
                "cholesterol_mg": 75
            }
        },
        {
            "name": "Chocolate Chip Cookies",
            "description": "Classic soft and chewy cookies loaded with chocolate chips",
            "cuisine_type": "American",
            "difficulty": "easy",
            "prep_time": 15,
            "cook_time": 12,
            "servings": 24,
            "diet_types": ["vegetarian"],
            "ingredients": [
                {"name": "all-purpose flour", "quantity": 2.25, "unit": "cups"},
                {"name": "butter", "quantity": 1, "unit": "cup", "notes": "softened"},
                {"name": "brown sugar", "quantity": 0.75, "unit": "cup"},
                {"name": "granulated sugar", "quantity": 0.75, "unit": "cup"},
                {"name": "eggs", "quantity": 2, "unit": "whole"},
                {"name": "vanilla extract", "quantity": 2, "unit": "tsp"},
                {"name": "baking soda", "quantity": 1, "unit": "tsp"},
                {"name": "salt", "quantity": 1, "unit": "tsp"},
                {"name": "chocolate chips", "quantity": 2, "unit": "cups"},
            ],
            "instructions": {
                "steps": [
                    "Preheat oven to 375F",
                    "Cream butter and sugars until fluffy",
                    "Beat in eggs and vanilla",
                    "Mix flour, baking soda, and salt",
                    "Gradually blend into butter mixture",
                    "Stir in chocolate chips",
                    "Drop rounded tablespoons onto baking sheets",
                    "Bake 9-11 minutes until golden",
                    "Cool on baking sheet 2 minutes",
                    "Transfer to wire rack"
                ],
                "tips": ["Chill dough 30 minutes for thicker cookies", "Slightly underbake for softer centers"]
            },
            "nutritional_info": {
                "calories": 215,
                "protein_g": 2,
                "carbohydrates_g": 28,
                "fat_g": 11,
                "fiber_g": 1,
                "sugar_g": 18,
                "sodium_mg": 180,
                "cholesterol_mg": 35
            }
        },
        {
            "name": "Panna Cotta with Berry Sauce",
            "description": "Italian cream dessert with fresh berry compote",
            "cuisine_type": "Italian",
            "difficulty": "medium",
            "prep_time": 20,
            "cook_time": 10,
            "servings": 6,
            "diet_types": ["vegetarian", "gluten-free"],
            "ingredients": [
                {"name": "heavy cream", "quantity": 2, "unit": "cups"},
                {"name": "sugar", "quantity": 0.5, "unit": "cup"},
                {"name": "vanilla bean", "quantity": 1, "unit": "whole", "notes": "split"},
                {"name": "gelatin", "quantity": 2.5, "unit": "tsp"},
                {"name": "mixed berries", "quantity": 2, "unit": "cups"},
                {"name": "lemon juice", "quantity": 1, "unit": "tbsp"},
                {"name": "honey", "quantity": 2, "unit": "tbsp"},
            ],
            "instructions": {
                "steps": [
                    "Bloom gelatin in cold water 5 minutes",
                    "Heat cream, sugar, and vanilla to simmer",
                    "Remove from heat, whisk in gelatin until dissolved",
                    "Strain into 6 ramekins or molds",
                    "Refrigerate at least 4 hours until set",
                    "Simmer berries with lemon juice and honey 10 minutes",
                    "Cool berry sauce",
                    "Unmold panna cotta onto plates",
                    "Spoon berry sauce over top"
                ],
                "tips": ["Can leave in ramekins instead of unmolding", "Lightly oil molds for easier unmolding"]
            },
            "nutritional_info": {
                "calories": 320,
                "protein_g": 3,
                "carbohydrates_g": 28,
                "fat_g": 23,
                "fiber_g": 2,
                "sugar_g": 24,
                "sodium_mg": 35,
                "cholesterol_mg": 85
            }
        },
        {
            "name": "Banana Foster",
            "description": "Flambéed bananas in rum caramel sauce over ice cream",
            "cuisine_type": "American",
            "difficulty": "medium",
            "prep_time": 10,
            "cook_time": 10,
            "servings": 4,
            "diet_types": ["vegetarian", "gluten-free"],
            "ingredients": [
                {"name": "bananas", "quantity": 4, "unit": "whole", "notes": "sliced"},
                {"name": "butter", "quantity": 0.25, "unit": "cup"},
                {"name": "brown sugar", "quantity": 0.5, "unit": "cup"},
                {"name": "cinnamon", "quantity": 0.5, "unit": "tsp"},
                {"name": "dark rum", "quantity": 0.25, "unit": "cup"},
                {"name": "vanilla ice cream", "quantity": 4, "unit": "scoops"},
                {"name": "heavy cream", "quantity": 0.25, "unit": "cup"},
            ],
            "instructions": {
                "steps": [
                    "Melt butter in large skillet",
                    "Add brown sugar and cinnamon, stir until dissolved",
                    "Add bananas, cook 2 minutes per side",
                    "Add rum, carefully ignite",
                    "Let flames subside",
                    "Stir in cream",
                    "Serve immediately over vanilla ice cream"
                ],
                "tips": ["Remove pan from heat before adding rum", "Be very careful when flambéing"]
            },
            "nutritional_info": {
                "calories": 445,
                "protein_g": 3,
                "carbohydrates_g": 62,
                "fat_g": 20,
                "fiber_g": 3,
                "sugar_g": 48,
                "sodium_mg": 125,
                "cholesterol_mg": 75
            }
        },
        {
            "name": "Key Lime Pie",
            "description": "Tart and creamy Florida-style lime pie",
            "cuisine_type": "American",
            "difficulty": "medium",
            "prep_time": 25,
            "cook_time": 20,
            "servings": 8,
            "diet_types": ["vegetarian"],
            "ingredients": [
                {"name": "graham cracker crust", "quantity": 1, "unit": "whole", "notes": "9-inch"},
                {"name": "sweetened condensed milk", "quantity": 1, "unit": "can", "notes": "14 oz"},
                {"name": "egg yolks", "quantity": 4, "unit": "whole"},
                {"name": "key lime juice", "quantity": 0.5, "unit": "cup"},
                {"name": "lime zest", "quantity": 1, "unit": "tbsp"},
                {"name": "heavy cream", "quantity": 1, "unit": "cup"},
                {"name": "powdered sugar", "quantity": 2, "unit": "tbsp"},
            ],
            "instructions": {
                "steps": [
                    "Preheat oven to 350F",
                    "Whisk together condensed milk, egg yolks, lime juice, zest",
                    "Pour into graham cracker crust",
                    "Bake 15-17 minutes until just set",
                    "Cool completely, then refrigerate 3 hours",
                    "Whip cream with powdered sugar to stiff peaks",
                    "Top pie with whipped cream",
                    "Garnish with lime zest"
                ],
                "tips": ["Key limes are more tart than regular limes", "Don't overbake or filling will be grainy"]
            },
            "nutritional_info": {
                "calories": 420,
                "protein_g": 7,
                "carbohydrates_g": 52,
                "fat_g": 20,
                "fiber_g": 1,
                "sugar_g": 42,
                "sodium_mg": 220,
                "cholesterol_mg": 165
            }
        }
    ]

    SALAD_RECIPES = [
        {
            "name": "Caesar Salad",
            "description": "Classic romaine salad with parmesan and garlicky dressing",
            "cuisine_type": "American",
            "difficulty": "easy",
            "prep_time": 20,
            "cook_time": 10,
            "servings": 4,
            "diet_types": ["vegetarian"],
            "ingredients": [
                {"name": "romaine lettuce", "quantity": 2, "unit": "heads", "notes": "chopped"},
                {"name": "parmesan cheese", "quantity": 0.5, "unit": "cup", "notes": "shaved"},
                {"name": "croutons", "quantity": 2, "unit": "cups"},
                {"name": "egg yolks", "quantity": 2, "unit": "whole"},
                {"name": "lemon juice", "quantity": 2, "unit": "tbsp"},
                {"name": "garlic", "quantity": 2, "unit": "cloves", "notes": "minced"},
                {"name": "Dijon mustard", "quantity": 1, "unit": "tsp"},
                {"name": "olive oil", "quantity": 0.5, "unit": "cup"},
                {"name": "anchovy paste", "quantity": 1, "unit": "tsp"},
            ],
            "instructions": {
                "steps": [
                    "Make croutons: toss bread cubes with oil, bake until golden",
                    "Whisk together egg yolks, lemon juice, garlic, mustard, anchovy",
                    "Slowly drizzle in olive oil while whisking",
                    "Season dressing with salt and pepper",
                    "Toss romaine with dressing",
                    "Top with parmesan and croutons",
                    "Serve immediately"
                ],
                "tips": ["Use pasteurized eggs for safety", "Dressing can be made ahead"]
            },
            "nutritional_info": {
                "calories": 385,
                "protein_g": 10,
                "carbohydrates_g": 18,
                "fat_g": 31,
                "fiber_g": 3,
                "sugar_g": 2,
                "sodium_mg": 520,
                "cholesterol_mg": 115
            }
        },
        {
            "name": "Greek Salad",
            "description": "Mediterranean salad with feta, olives, and lemon dressing",
            "cuisine_type": "Greek",
            "difficulty": "easy",
            "prep_time": 15,
            "cook_time": 0,
            "servings": 6,
            "diet_types": ["vegetarian", "gluten-free"],
            "ingredients": [
                {"name": "cucumbers", "quantity": 2, "unit": "whole", "notes": "diced"},
                {"name": "tomatoes", "quantity": 4, "unit": "whole", "notes": "diced"},
                {"name": "red onion", "quantity": 1, "unit": "whole", "notes": "sliced"},
                {"name": "bell pepper", "quantity": 1, "unit": "whole", "notes": "diced"},
                {"name": "kalamata olives", "quantity": 1, "unit": "cup"},
                {"name": "feta cheese", "quantity": 1, "unit": "cup", "notes": "crumbled"},
                {"name": "olive oil", "quantity": 0.25, "unit": "cup"},
                {"name": "lemon juice", "quantity": 2, "unit": "tbsp"},
                {"name": "dried oregano", "quantity": 1, "unit": "tsp"},
            ],
            "instructions": {
                "steps": [
                    "Combine cucumbers, tomatoes, onion, pepper, olives in bowl",
                    "Whisk together olive oil, lemon juice, oregano",
                    "Pour dressing over vegetables",
                    "Top with crumbled feta",
                    "Let sit 10 minutes before serving",
                    "Serve at room temperature"
                ],
                "tips": ["Don't refrigerate - best at room temperature"]
            },
            "nutritional_info": {
                "calories": 220,
                "protein_g": 6,
                "carbohydrates_g": 12,
                "fat_g": 17,
                "fiber_g": 3,
                "sugar_g": 6,
                "sodium_mg": 620,
                "cholesterol_mg": 25
            }
        },
        {
            "name": "Caprese Salad",
            "description": "Simple Italian salad with tomatoes, mozzarella, and basil",
            "cuisine_type": "Italian",
            "difficulty": "easy",
            "prep_time": 10,
            "cook_time": 0,
            "servings": 4,
            "diet_types": ["vegetarian", "gluten-free", "low-carb"],
            "ingredients": [
                {"name": "tomatoes", "quantity": 4, "unit": "whole", "notes": "large, sliced"},
                {"name": "fresh mozzarella", "quantity": 16, "unit": "oz", "notes": "sliced"},
                {"name": "fresh basil", "quantity": 0.5, "unit": "cup", "notes": "leaves"},
                {"name": "extra virgin olive oil", "quantity": 0.25, "unit": "cup"},
                {"name": "balsamic glaze", "quantity": 2, "unit": "tbsp"},
                {"name": "salt", "quantity": 0.5, "unit": "tsp"},
                {"name": "black pepper", "quantity": 0.25, "unit": "tsp"},
            ],
            "instructions": {
                "steps": [
                    "Arrange tomato and mozzarella slices on platter",
                    "Tuck basil leaves between slices",
                    "Drizzle with olive oil and balsamic glaze",
                    "Season with salt and pepper",
                    "Let sit 10 minutes before serving",
                    "Serve at room temperature"
                ],
                "tips": ["Use the ripest tomatoes available", "Quality olive oil makes all the difference"]
            },
            "nutritional_info": {
                "calories": 285,
                "protein_g": 14,
                "carbohydrates_g": 8,
                "fat_g": 22,
                "fiber_g": 2,
                "sugar_g": 5,
                "sodium_mg": 420,
                "cholesterol_mg": 45
            }
        },
        {
            "name": "Asian Sesame Noodle Salad",
            "description": "Cold noodles with vegetables in sesame-ginger dressing",
            "cuisine_type": "Asian",
            "difficulty": "easy",
            "prep_time": 20,
            "cook_time": 10,
            "servings": 6,
            "diet_types": ["vegan"],
            "ingredients": [
                {"name": "soba noodles", "quantity": 12, "unit": "oz"},
                {"name": "red cabbage", "quantity": 2, "unit": "cups", "notes": "shredded"},
                {"name": "carrots", "quantity": 2, "unit": "whole", "notes": "julienned"},
                {"name": "edamame", "quantity": 1, "unit": "cup", "notes": "shelled"},
                {"name": "scallions", "quantity": 4, "unit": "whole", "notes": "sliced"},
                {"name": "sesame oil", "quantity": 3, "unit": "tbsp"},
                {"name": "soy sauce", "quantity": 3, "unit": "tbsp"},
                {"name": "rice vinegar", "quantity": 2, "unit": "tbsp"},
                {"name": "fresh ginger", "quantity": 1, "unit": "tbsp", "notes": "grated"},
                {"name": "sesame seeds", "quantity": 2, "unit": "tbsp", "notes": "toasted"},
            ],
            "instructions": {
                "steps": [
                    "Cook soba noodles according to package",
                    "Rinse under cold water, drain well",
                    "Whisk together sesame oil, soy sauce, vinegar, ginger",
                    "Toss noodles with cabbage, carrots, edamame",
                    "Pour dressing over salad, toss well",
                    "Garnish with scallions and sesame seeds",
                    "Serve chilled or at room temperature"
                ],
                "tips": ["Can add protein like tofu or chicken", "Best made ahead to let flavors develop"]
            },
            "nutritional_info": {
                "calories": 285,
                "protein_g": 11,
                "carbohydrates_g": 42,
                "fat_g": 9,
                "fiber_g": 5,
                "sugar_g": 5,
                "sodium_mg": 680,
                "cholesterol_mg": 0
            }
        },
        {
            "name": "Roasted Vegetable Quinoa Salad",
            "description": "Warm grain salad with roasted vegetables and lemon vinaigrette",
            "cuisine_type": "Mediterranean",
            "difficulty": "medium",
            "prep_time": 20,
            "cook_time": 30,
            "servings": 6,
            "diet_types": ["vegan", "gluten-free"],
            "ingredients": [
                {"name": "quinoa", "quantity": 1.5, "unit": "cups"},
                {"name": "zucchini", "quantity": 2, "unit": "whole", "notes": "diced"},
                {"name": "bell peppers", "quantity": 2, "unit": "whole", "notes": "diced"},
                {"name": "red onion", "quantity": 1, "unit": "whole", "notes": "diced"},
                {"name": "cherry tomatoes", "quantity": 2, "unit": "cups", "notes": "halved"},
                {"name": "olive oil", "quantity": 0.5, "unit": "cup"},
                {"name": "lemon juice", "quantity": 3, "unit": "tbsp"},
                {"name": "fresh herbs", "quantity": 0.5, "unit": "cup", "notes": "mixed, chopped"},
            ],
            "instructions": {
                "steps": [
                    "Cook quinoa according to package",
                    "Toss vegetables with olive oil, salt, pepper",
                    "Roast at 425F for 25 minutes",
                    "Whisk together remaining oil, lemon juice, herbs",
                    "Combine quinoa and roasted vegetables",
                    "Pour dressing over salad, toss well",
                    "Serve warm or room temperature"
                ],
                "tips": ["Can make ahead and serve cold", "Add feta or goat cheese for extra richness"]
            },
            "nutritional_info": {
                "calories": 320,
                "protein_g": 8,
                "carbohydrates_g": 38,
                "fat_g": 16,
                "fiber_g": 6,
                "sugar_g": 6,
                "sodium_mg": 280,
                "cholesterol_mg": 0
            }
        }
    ]

    BEVERAGE_RECIPES = [
        {
            "name": "Mango Lassi",
            "description": "Indian yogurt smoothie with ripe mango and cardamom",
            "cuisine_type": "Indian",
            "difficulty": "easy",
            "prep_time": 5,
            "cook_time": 0,
            "servings": 4,
            "diet_types": ["vegetarian", "gluten-free"],
            "ingredients": [
                {"name": "ripe mangoes", "quantity": 2, "unit": "whole", "notes": "peeled and diced"},
                {"name": "plain yogurt", "quantity": 2, "unit": "cups"},
                {"name": "milk", "quantity": 1, "unit": "cup"},
                {"name": "sugar", "quantity": 3, "unit": "tbsp"},
                {"name": "cardamom", "quantity": 0.25, "unit": "tsp", "notes": "ground"},
                {"name": "ice cubes", "quantity": 1, "unit": "cup"},
            ],
            "instructions": {
                "steps": [
                    "Combine mango, yogurt, milk, sugar, cardamom in blender",
                    "Blend until smooth",
                    "Add ice cubes and blend again",
                    "Taste and adjust sweetness",
                    "Pour into glasses",
                    "Serve immediately, garnished with mint"
                ],
                "tips": ["Use frozen mango for thicker consistency", "Adjust sugar based on mango sweetness"]
            },
            "nutritional_info": {
                "calories": 185,
                "protein_g": 6,
                "carbohydrates_g": 36,
                "fat_g": 3,
                "fiber_g": 2,
                "sugar_g": 32,
                "sodium_mg": 85,
                "cholesterol_mg": 12
            }
        },
        {
            "name": "Classic Mojito",
            "description": "Refreshing Cuban cocktail with mint, lime, and rum",
            "cuisine_type": "Cuban",
            "difficulty": "easy",
            "prep_time": 5,
            "cook_time": 0,
            "servings": 1,
            "diet_types": ["vegan", "gluten-free"],
            "ingredients": [
                {"name": "fresh mint leaves", "quantity": 10, "unit": "leaves"},
                {"name": "lime", "quantity": 1, "unit": "whole", "notes": "cut into wedges"},
                {"name": "white sugar", "quantity": 2, "unit": "tsp"},
                {"name": "white rum", "quantity": 2, "unit": "oz"},
                {"name": "club soda", "quantity": 4, "unit": "oz"},
                {"name": "ice cubes", "quantity": 1, "unit": "cup"},
            ],
            "instructions": {
                "steps": [
                    "Muddle mint leaves and sugar in glass",
                    "Add lime wedges and muddle again",
                    "Fill glass with ice",
                    "Pour rum over ice",
                    "Top with club soda",
                    "Stir gently",
                    "Garnish with mint sprig and lime wheel"
                ],
                "tips": ["Don't over-muddle mint or it will taste bitter", "Use fresh lime juice only"]
            },
            "nutritional_info": {
                "calories": 165,
                "protein_g": 0,
                "carbohydrates_g": 12,
                "fat_g": 0,
                "fiber_g": 1,
                "sugar_g": 10,
                "sodium_mg": 15,
                "cholesterol_mg": 0
            }
        },
        {
            "name": "Green Smoothie",
            "description": "Healthy smoothie with spinach, banana, and tropical fruits",
            "cuisine_type": "American",
            "difficulty": "easy",
            "prep_time": 5,
            "cook_time": 0,
            "servings": 2,
            "diet_types": ["vegan", "gluten-free"],
            "ingredients": [
                {"name": "fresh spinach", "quantity": 2, "unit": "cups"},
                {"name": "frozen banana", "quantity": 1, "unit": "whole"},
                {"name": "frozen mango", "quantity": 1, "unit": "cup"},
                {"name": "pineapple", "quantity": 0.5, "unit": "cup"},
                {"name": "coconut water", "quantity": 1, "unit": "cup"},
                {"name": "chia seeds", "quantity": 1, "unit": "tbsp"},
            ],
            "instructions": {
                "steps": [
                    "Add coconut water to blender first",
                    "Add spinach and blend until smooth",
                    "Add frozen fruits and chia seeds",
                    "Blend until completely smooth",
                    "Add more liquid if too thick",
                    "Pour into glasses and serve immediately"
                ],
                "tips": ["Freeze ripe bananas ahead for creamier texture", "Add protein powder for post-workout boost"]
            },
            "nutritional_info": {
                "calories": 165,
                "protein_g": 3,
                "carbohydrates_g": 38,
                "fat_g": 2,
                "fiber_g": 6,
                "sugar_g": 26,
                "sodium_mg": 135,
                "cholesterol_mg": 0
            }
        },
        {
            "name": "Iced Matcha Latte",
            "description": "Japanese green tea latte served over ice",
            "cuisine_type": "Japanese",
            "difficulty": "easy",
            "prep_time": 5,
            "cook_time": 0,
            "servings": 1,
            "diet_types": ["vegetarian", "gluten-free"],
            "ingredients": [
                {"name": "matcha powder", "quantity": 1, "unit": "tsp"},
                {"name": "hot water", "quantity": 2, "unit": "tbsp"},
                {"name": "milk", "quantity": 1, "unit": "cup"},
                {"name": "honey", "quantity": 1, "unit": "tbsp"},
                {"name": "ice cubes", "quantity": 1, "unit": "cup"},
            ],
            "instructions": {
                "steps": [
                    "Sift matcha powder into small bowl",
                    "Add hot water and whisk vigorously until smooth",
                    "Fill glass with ice",
                    "Pour milk over ice",
                    "Stir in honey until dissolved",
                    "Pour matcha mixture over milk",
                    "Stir and serve immediately"
                ],
                "tips": ["Use bamboo whisk for traditional preparation", "Use almond or oat milk for vegan version"]
            },
            "nutritional_info": {
                "calories": 145,
                "protein_g": 8,
                "carbohydrates_g": 24,
                "fat_g": 2.5,
                "fiber_g": 1,
                "sugar_g": 22,
                "sodium_mg": 105,
                "cholesterol_mg": 12
            }
        },
        {
            "name": "Fresh Lemonade",
            "description": "Classic homemade lemonade with fresh squeezed lemons",
            "cuisine_type": "American",
            "difficulty": "easy",
            "prep_time": 10,
            "cook_time": 5,
            "servings": 8,
            "diet_types": ["vegan", "gluten-free"],
            "ingredients": [
                {"name": "lemons", "quantity": 8, "unit": "whole"},
                {"name": "sugar", "quantity": 1.5, "unit": "cups"},
                {"name": "water", "quantity": 8, "unit": "cups"},
                {"name": "ice cubes", "quantity": 4, "unit": "cups"},
            ],
            "instructions": {
                "steps": [
                    "Make simple syrup: heat 1 cup water and sugar until dissolved",
                    "Cool syrup completely",
                    "Juice lemons to get 1.5 cups juice",
                    "Combine lemon juice, simple syrup, and remaining water",
                    "Stir well and taste",
                    "Adjust sweetness if needed",
                    "Serve over ice with lemon slices"
                ],
                "tips": ["Roll lemons on counter before juicing", "Add fresh herbs like mint or basil for variation"]
            },
            "nutritional_info": {
                "calories": 145,
                "protein_g": 0,
                "carbohydrates_g": 38,
                "fat_g": 0,
                "fiber_g": 0,
                "sugar_g": 36,
                "sodium_mg": 10,
                "cholesterol_mg": 0
            }
        }
    ]

    def __init__(self, seed: int = None):
        """Initialize recipe generator with optional random seed."""
        if seed:
            random.seed(seed)

    def get_all_recipes(self) -> list[dict[str, Any]]:
        """Get all recipe templates combined."""
        return (
            self.BREAKFAST_RECIPES
            + self.MAIN_COURSE_RECIPES
            + self.APPETIZER_RECIPES
            + self.DESSERT_RECIPES
            + self.SALAD_RECIPES
            + self.BEVERAGE_RECIPES
        )

    def generate_recipes(
        self, count: int, categories: list[str] = None, seed: int = None
    ) -> list[dict[str, Any]]:
        """Generate specified number of recipes.

        Args:
            count: Number of recipes to generate
            categories: Optional list of categories to filter by
            seed: Optional random seed for reproducibility

        Returns:
            List of recipe dictionaries
        """
        if seed:
            random.seed(seed)

        all_recipes = self.get_all_recipes()

        # If categories specified, filter
        if categories:
            # For this implementation, we'll just return all and let caller decide
            pass

        # If requesting more recipes than available, repeat with variations
        if count > len(all_recipes):
            recipes = all_recipes.copy()
            # Add variations by repeating and modifying slightly
            while len(recipes) < count:
                base_recipe = random.choice(all_recipes).copy()
                # Add variation marker to name
                base_recipe["name"] = f"{base_recipe['name']} (Variation)"
                recipes.append(base_recipe)
        else:
            recipes = random.sample(all_recipes, count)

        return recipes

    def get_category_distribution(self) -> dict[str, int]:
        """Get the number of recipes in each category."""
        return {
            "Breakfast & Brunch": len(self.BREAKFAST_RECIPES),
            "Main Courses": len(self.MAIN_COURSE_RECIPES),
            "Appetizers & Snacks": len(self.APPETIZER_RECIPES),
            "Desserts": len(self.DESSERT_RECIPES),
            "Salads & Sides": len(self.SALAD_RECIPES),
            "Beverages": len(self.BEVERAGE_RECIPES),
        }

    def get_recipes_by_diet_type(self, diet_type: str) -> list[dict[str, Any]]:
        """Get all recipes matching a specific diet type."""
        all_recipes = self.get_all_recipes()
        return [r for r in all_recipes if diet_type in r.get("diet_types", [])]

    def get_recipes_by_difficulty(self, difficulty: str) -> list[dict[str, Any]]:
        """Get all recipes of a specific difficulty level."""
        all_recipes = self.get_all_recipes()
        return [r for r in all_recipes if r.get("difficulty") == difficulty]
