class Card:
    card_number = 0

    @classmethod
    def gen_card_id(cls):
        card_id = cls.card_number
        cls.card_number += 1
        
        return card_id

    def __init__(self, company_name: str, owner_name: str):
        self.company_name = company_name
        self.owner_name = owner_name
        self.card_id = self.gen_card_id()
        self.balance = 0

    # 지불하기
    def pay(self, amount : int) -> bool:
        # 카드로 금액을 결제할 때 잔액이 충분하면 금액을 차감하고 True를 반환하고 잔액이 부족하면 결제를 취소하고 False를 반환함
        if self.balance >= amount:
            self.balance -= amount
            return True
        else:
            return False
    
    # 충전하기
    def recharge(self, amount : int):
        self.balance += amount

    # 카드의 정보 읽기
    def get_info(self):
        return self.company_name, self.owner_name, self.card_id
    
    # 카드의 잔액을 반환
    def get_balance(self) -> int:
        return self.balance

    def __str__(self):
        return (f"Card(company_name={self.company_name}, owner_name={self.owner_name}, "
                f"card_number={self.card_number}, balance={self.balance})")

# 첫 번째 카드
company_name_1 = "농협카드"
user_name_1 = "Michel"
card1 = Card(company_name_1, user_name_1)

# 두 번째 카드
company_name_2 = "롯데카드"
user_name_2 = "Hamilton"
card2 = Card(company_name_2, user_name_2)

# 카드 정보 읽기
print(card1.get_info())
print(card2.get_info())

# 잔액 확인
print(card1.get_balance())
print(card2.get_balance())

# 잔액 충전
card1.recharge(50000)
card2.recharge(10000)

# 잔액 소비
print("Card1의 결제 여부 : ", str(card1.pay(30000)))
print("Card2의 결제 여부 : ", str(card2.pay(30000)))

# 잔액 확인
print(card1.get_balance())
print(card2.get_balance())