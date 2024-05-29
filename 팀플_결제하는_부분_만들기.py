class Card:
    def __init__(self, company_name: str, balance: float):
        self.company_name = company_name
        self.balance = balance
        self.owner_name = None
        self.card_number = None
        self.cvs = None

    def set_card_details(self, owner_name: str, card_number: str, cvs: str):
        self.owner_name = owner_name
        self.card_number = card_number
        self.cvs = cvs

    def charge(self, amount: float) -> bool:
        # 카드로 금액을 결제할 때 잔액이 충분하면 금액을 차감하고 True를 반환하고 잔액이 부족하면 결제를 취소하고 False를 반환함
        if self.balance >= amount:
            self.balance -= amount
            return True
        else:
            return False

    def get_balance(self) -> float:
        # 카드의 잔액을 반환
        return self.balance

    def __str__(self):
        return (f"Card(company_name={self.company_name}, owner_name={self.owner_name}, "
                f"card_number={self.card_number}, balance={self.balance})")


class PaymentProcessor:
    def __init__(self, card: Card):
        self.card = card

    def process_payment(self, amount: float, flight_info: str) -> str:
        """
        결제를 처리하고, 결과를 반환합니다.
        """
        if self.card.charge(amount):
            return (f"결제가 완료되었습니다.\n"
                    f"항공권 정보: {flight_info}\n"
                    f"결제 금액: {amount}원\n"
                    f"잔액: {self.card.get_balance()}원")
        else:
            return "잔액이 부족하여 결제에 실패했습니다."


# 여러 카드 클래스를 인스턴스화 (싱글턴 패턴 제거 후)

# 첫 번째 카드
company_name_1 = "Visa"
initial_balance_1 = 100000
card1 = Card(company_name_1, initial_balance_1)

# 두 번째 카드
company_name_2 = "MasterCard"
initial_balance_2 = 200000
card2 = Card(company_name_2, initial_balance_2)

# 첫 번째 카드 소유자 이름 작성 및 정보 설정
owner_name_1 = input("첫 번째 카드 소유자 이름을 입력하세요: ")

# 첫 번째 카드 번호 입력 및 유효성 검사
while True:
    card_number_1 = input("첫 번째 카드 번호를 입력하세요 (16자리): ")
    if len(card_number_1) == 16 and card_number_1.isdigit():
        break
    else:
        print("유효하지 않은 카드 번호입니다. 16자리 숫자로 입력하세요.")

# 첫 번째 CVS 번호 입력 및 유효성 검사
while True:
    cvs_1 = input("첫 번째 CVS 번호를 입력하세요 (3자리): ")
    if len(cvs_1) == 3 and cvs_1.isdigit():
        break
    else:
        print("유효하지 않은 CVS 번호입니다. 3자리 숫자로 입력하세요.")

# 첫 번째 카드 정보 설정
card1.set_card_details(owner_name_1, card_number_1, cvs_1)

# 두 번째 카드 소유자 이름 작성 및 정보 설정
owner_name_2 = input("두 번째 카드 소유자 이름을 입력하세요: ")

# 두 번째 카드 번호 입력 및 유효성 검사
while True:
    card_number_2 = input("두 번째 카드 번호를 입력하세요 (16자리): ")
    if len(card_number_2) == 16 and card_number_2.isdigit():
        break
    else:
        print("유효하지 않은 카드 번호입니다. 16자리 숫자로 입력하세요.")

# 두 번째 CVS 번호 입력 및 유효성 검사
while True:
    cvs_2 = input("두 번째 CVS 번호를 입력하세요 (3자리): ")
    if len(cvs_2) == 3 and cvs_2.isdigit():
        break
    else:
        print("유효하지 않은 CVS 번호입니다. 3자리 숫자로 입력하세요.")

# 두 번째 카드 정보 설정
card2.set_card_details(owner_name_2, card_number_2, cvs_2)

# 첫 번째 결제 처리기 생성
payment_processor1 = PaymentProcessor(card1)

# 두 번째 결제 처리기 생성
payment_processor2 = PaymentProcessor(card2)

# 항공권 정보 및 결제 금액(어차피 엑셀에서 가져올 정보라서 그냥 임의로 입력)
flight_info = "서울 -> 도쿄, 2024-07-01, 좌석: 23A"
payment_amount = 50000

# 첫 번째 카드로 결제 처리 및 결과 출력
result1 = payment_processor1.process_payment(payment_amount, flight_info)
print(result1)

# 두 번째 카드로 결제 처리 및 결과 출력
result2 = payment_processor2.process_payment(payment_amount, flight_info)
print(result2)
