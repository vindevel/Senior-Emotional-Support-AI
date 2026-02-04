from db.database_connect import get_db_connection
from db.user_lookup import get_all_users

#-----------------------중복확인---------------------
def is_duplicate_user_guardian(username, birth_year, phone_number):
    """같은 이름 + 출생 연도 + 전화번호를 가진 사용자가 있는지 확인"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) FROM users 
        WHERE username = %s AND birth_year = %s AND phone_number = %s
    """, (username, birth_year, phone_number))
    
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0  #1명 이상이면 중복됨 (True 반환)

#----------------------db 추가-----------------------
def add_user(username, birth_year, gender, role, phone_number):
    """신규 사용자 또는 보호자를 users 테이블에 추가"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users (username, birth_year, gender, role, phone_number) 
        VALUES (%s, %s, %s, %s, %s)
    """, (username, birth_year, gender, role, phone_number))
    
    conn.commit()
    user_id = cursor.lastrowid  #생성된 사용자 ID 가져오기
    conn.close()
    
    return user_id

def add_guardian_relation(user_id, guardian_id):
    """user_guardians 테이블에 보호자 관계 추가"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO user_guardians (user_id, guardian_id) VALUES (%s, %s)
    """, (user_id, guardian_id))
    
    conn.commit()
    conn.close()

#-----------------사용자,보호자 추가------------------
def select_or_create_user():
    """기존 사용자 선택 또는 신규 사용자 & 보호자 추가"""
    users = get_all_users()
    print("\n초기 설정을 진행합니다.")

    if users:
        print("\n※ 기존 사용자 목록:")
        for idx, (user_id, username, birth_year, phone_number) in enumerate(users, 1):
            phone_display = phone_number if phone_number else "전화번호 없음"
            print(f"{idx}. {username} ({birth_year}, {phone_display})")

        while True:
            choice = input("\n사용자를 선택하세요 (번호 입력, 신규 사용자는 0 입력): ").strip()

            if choice.isdigit():
                choice = int(choice)
                if 1 <= choice <= len(users):
                    selected_user = users[choice - 1]  # (id, username, birth_year, phone_number)
                    print(f"\n▶ '{selected_user[1]}'님을 선택하셨습니다.")
                    return selected_user
                elif choice == 0:
                    break
            print("[경고] 잘못된 입력입니다. 다시 입력하세요.")

    print("\n※ 신규 사용자 정보를 입력하세요.")

    #사용자 정보 입력
    while True:
        username = input("사용자 이름: ").strip()
        
        #출생 연도 숫자 예외 처리
        while True:
            user_birth_year = input("출생 연도 (YYYY 형식): ").strip()
            if user_birth_year.isdigit() and len(user_birth_year) == 4:
                user_birth_year = int(user_birth_year)
                break
            print("[경고] 출생 연도는 4자리 숫자로 입력해야 합니다.")

        #성별 입력 (남 또는 여)
        while True:
            gender = input("성별 ('남' 또는 '여' 입력): ").strip()
            if gender in ['남', '여']:
                break
            print("[경고] 성별은 '남' 또는 '여'로 입력해야 합니다.")

        #전화번호 입력 (없으면 None)
        phone_number = input("전화번호 (없으면 Enter): ").strip() or None

        #사용자 중복 체크
        if is_duplicate_user_guardian(username, user_birth_year, phone_number):
            print("[경고] 동일한 사용자 또는 보호자가 이미 존재합니다. 다시 입력하세요.")
            continue
        break

    #사용자 추가
    user_id = add_user(username, user_birth_year, gender, "사용자", phone_number)

    print("\n※ 보호자 정보를 입력하세요.")

    #보호자 정보 입력
    guardian_name = input("보호자 이름: ").strip()

    #보호자 출생 연도 예외 처리
    while True:
        guardian_birth_year = input("보호자 출생 연도 (YYYY 형식): ").strip()
        if guardian_birth_year.isdigit() and len(guardian_birth_year) == 4:
            guardian_birth_year = int(guardian_birth_year)
            break
        print("[경고] 출생 연도는 4자리 숫자로 입력해야 합니다.")

    #보호자 성별 입력
    while True:
        guardian_gender = input("보호자 성별 ('남' 또는 '여' 입력): ").strip()
        if guardian_gender in ['남', '여']:
            break
        print("[경고] 성별은 '남' 또는 '여'로 입력해야 합니다.")

    #보호자 전화번호 입력 (필수)
    while True:
        guardian_phone = input("보호자 전화번호 (필수 입력): ").strip()
        if guardian_phone:
            break
        print("[경고] 보호자 전화번호는 필수 입력입니다.")

    #보호자 추가
    guardian_id = add_user(guardian_name, guardian_birth_year, guardian_gender, "보호자", guardian_phone)

    #사용자-보호자 관계 저장
    add_guardian_relation(user_id, guardian_id)

    user_phone_display = phone_number if phone_number else "전화번호 없음"

    print(f"\n▶ '{username}'님이 등록되었습니다. (출생연도: {user_birth_year}, 성별: {gender}, 전화번호: {user_phone_display})")
    print(f"▶ 보호자 '{guardian_name}'님이 등록되었습니다. (출생연도: {guardian_birth_year}, 성별: {guardian_gender}, 전화번호: {guardian_phone})")

    return (user_id, username, user_birth_year, phone_number)

