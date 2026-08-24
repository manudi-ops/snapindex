from app import app
from neglect.engine import build_category_features, detect_neglect
from db.models import Category

with app.app_context():
    category_ids, features = build_category_features(1)

    print("Raw features per category:")
    for cat_id, feat in zip(category_ids, features):
        cat = Category.query.get(cat_id)
        upload_count, open_count, days_since_access, access_ratio = feat
        print(f"  {cat.categoryName}: uploads={upload_count}, opens={open_count}, days_since_access={days_since_access:.2f}, access_ratio={access_ratio:.2f}")

    print()
    print("Detection result:")
    result = detect_neglect(1)
    print(result)