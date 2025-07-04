from apps.users.utils.jwt import generate_jwt_token_pair

if __name__ == "__main__":
    user_id = 123  # 테스트용 user_id를 실제 존재하는 값이나 임의 숫자로 넣어주세요
    tokens = generate_jwt_token_pair(user_id)
    print("Access Token:")
    print(tokens["access"])
    print("\nRefresh Token:")
    print(tokens["refresh"])
