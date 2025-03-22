import pandas as pd
import os
from dataset.models.cf_recommender import cf_model  # Giả định bạn đã có hàm này

# Định nghĩa các đường dẫn (giữ nguyên như code của bạn)
updated_reviews_path = r"C:\Users\OS\LAVY\  LAVY_FINALPROJECT\dataset\updated_reviews.csv"
model_path = r"C:\Users\OS\LAVY\LAVY_FINALPROJECT\dataset\models\svdmodel.zip"

# Hàm lưu đánh giá
def save_ratings(updated_df):
    """Lưu dữ liệu đánh giá vào file CSV."""
    try:
        updated_df.to_csv(updated_reviews_path, index=False)
        print(f"Saved ratings to {updated_reviews_path}")
        return True
    except Exception as e:
        print(f"Error saving ratings: {e}")
        return False

# Hàm tạo gợi ý (dùng lại từ code của bạn)
def generate_recommendations(df, num=10, location=None, name=None, text=None, model_path=model_path):
    """Tạo gợi ý dựa trên đánh giá của người dùng."""
    recommendations = cf_model(df=df, num=num, location=location, name=name, text=text, model_path=model_path)
    return recommendations

# Hàm giả lập dữ liệu và kiểm tra
def test_ratings_and_recommendations():
    # 1. Tạo dữ liệu giả lập ban đầu (mô phỏng self.reviews)
    reviews = pd.DataFrame({
        'business_id': ['b1', 'b2', 'b3', 'b4', 'b5'],
        'name': ['Nhà hàng A', 'Nhà hàng B', 'Nhà hàng C', 'Nhà hàng D', 'Nhà hàng E'],
        'location': ['Hà Nội', 'TP.HCM', 'Hà Nội', 'Đà Nẵng', 'Hà Nội'],
        'categories': ['Ý', 'Trung Quốc', 'Mexico', 'Việt Nam', 'Nhật Bản'],
        'bs_rating': [4.0, 4.2, 3.8, 4.5, 4.1],
        'user_rating': [None, None, None, None, None],
        'user_id': ['u1', 'u1', 'u1', 'u1', 'u1']
    })
    print("Dữ liệu ban đầu:")
    print(reviews)

    # 2. Giả lập người dùng nhập đánh giá (mô phỏng displayed_restaurants)
    displayed_restaurants = reviews.sample(3).copy()  # Chọn ngẫu nhiên 3 nhà hàng để đánh giá
    print("\nNhà hàng hiển thị để đánh giá:")
    print(displayed_restaurants)

    # Giả lập nhập đánh giá từ người dùng (thay vì GUI, dùng dữ liệu cứng)
    user_ratings = {
        displayed_restaurants.iloc[0]['business_id']: 4.5,
        displayed_restaurants.iloc[1]['business_id']: 3.0,
        displayed_restaurants.iloc[2]['business_id']: 5.0
    }

    # Cập nhật đánh giá vào displayed_restaurants
    for index, row in displayed_restaurants.iterrows():
        business_id = row['business_id']
        if business_id in user_ratings:
            displayed_restaurants.at[index, 'user_rating'] = user_ratings[business_id]

    print("\nSau khi người dùng đánh giá:")
    print(displayed_restaurants)

    # 3. Cập nhật đánh giá vào reviews
    for _, row in displayed_restaurants.iterrows():
        reviews.loc[reviews['business_id'] == row['business_id'], 'user_rating'] = row['user_rating']

    print("\nDữ liệu reviews sau khi cập nhật:")
    print(reviews)

    # 4. Lưu file đánh giá
    if not save_ratings(reviews):
        print("Không thể lưu file đánh giá!")
        return

    # 5. Tải lại dữ liệu từ file đã lưu
    try:
        updated_reviews = pd.read_csv(updated_reviews_path)
        print("\nDữ liệu tải từ file updated_reviews.csv:")
        print(updated_reviews)
    except Exception as e:
        print(f"Không thể tải file đánh giá: {e}")
        return

    # 6. Chạy mô hình CF với dữ liệu từ file
    try:
        recommendations = generate_recommendations(df=updated_reviews, num=3)  # Giới hạn 3 gợi ý để dễ kiểm tra
        print("\nKết quả gợi ý từ mô hình CF:")
        print(recommendations)
    except Exception as e:
        print(f"Lỗi khi chạy mô hình CF: {e}")

# Chạy thử
if __name__ == "__main__":
    test_ratings_and_recommendations()