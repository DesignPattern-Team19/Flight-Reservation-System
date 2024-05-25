class Ticket:
    def __init__(self):
        self.seat = None
        self.meal = None
        self.baggage = None

    def __str__(self):
        return f"좌석: {self.seat}, 기내식: {self.meal}, 수하물: {self.baggage}"


class TicketBuilder:
    def __init__(self):
        self.ticket = Ticket()

    def set_seat(self, seat):
        self.ticket.seat = seat
        return self

    def set_meal(self, meal):
        self.ticket.meal = meal
        return self

    def set_baggage(self, baggage):
        self.ticket.baggage = baggage
        return self

    def build(self):
        return self.ticket


def display_seat_options():
    rows = 55
    seats_per_row = 9
    seat_letters = 'ABCDEFGHI'
    for i in range(1, rows + 1):
        row_seats = []
        for j in range(seats_per_row):
            row_seats.append(f"{i}{seat_letters[j]}")
        for k in range(0, seats_per_row, 3):
            print(' '.join(row_seats[k:k+3]), end='   ')
        print()


def main():
    builder = TicketBuilder()

    print("좌석 선택 시 39,000원이 추가됩니다.")
    print("좌석을 선택하시겠습니까?")
    print("1. 예")
    print("2. 아니요")
    seat_choice = input("선택을 입력하세요: ")

    if seat_choice == '1':
        print("좌석을 선택하세요:")
        display_seat_options()
        seat = input("좌석을 입력하세요 (예: 1A, 1B, ... 55I): ")
        builder.set_seat(seat)
    else:
        builder.set_seat("좌석 선택 안함")

    print("\n기내식을 선택하세요:")
    meal_options = [
        "일반식", "저지방식", "당뇨식", "저열량식", "저자극식",
        "글루텐 제한식", "저염식", "유당제한식", "이슬람교식", "힌두교식", "유대교식"
    ]
    for i, meal in enumerate(meal_options, 1):
        print(f"{i}. {meal}")
    meal_choice = int(input("기내식 번호를 입력하세요: "))
    builder.set_meal(meal_options[meal_choice - 1])

    print("\n수하물 옵션을 선택하세요:")
    baggage_options = ["추가안함", "15kg 추가"]
    for i, baggage in enumerate(baggage_options, 1):
        print(f"{i}. {baggage}")
    baggage_choice = int(input("수하물 번호를 입력하세요: "))
    builder.set_baggage(baggage_options[baggage_choice - 1])

    ticket = builder.build()
    print("\n티켓 상세 정보:")
    print(ticket)


if __name__ == "__main__":
    main()
