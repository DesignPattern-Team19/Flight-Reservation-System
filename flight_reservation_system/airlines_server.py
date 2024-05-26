from abc import ABCMeta, abstractmethod
import pandas as pd

class server(metaclass = ABCMeta):
    @abstractmethod
    def check_flight_schedule_one_way(self, departure_date, departing_from, arriving_at):
        pass

    @abstractmethod
    def check_flight_schedule_round_trip(self, departure_date, return_date, departing_from, arriving_at):
        pass

    @abstractmethod
    def book_flight(self, out_bound_flight_id, in_bound_flight_id, passenger_count, passengers_info, payment_method_or_agencyID):
        pass

    @abstractmethod
    def cancel_flight(self, booking_reference):
        pass
    

# 1. 지연 로딩/즉시 로딩 측면
# 2. 중간에서 처리 측면
class Proxy_server(server):
    def __init__(self, server):
        self.airlines_server = server
        self.peak_season = None  # 여러개 일 경우 list()를 고려할 수 있음
        self.peak_season_flight_schedule = None

    def add_peak_season(self, start_date, end_date):
        df = self.airlines_server.flight_schedule
        
        self.peak_season = (start_date, end_date)
        self.peak_season_flight_schedule = df[(start_date <= df['Date']) & (df['Date'] <= end_date)]


    def check_flight_schedule_one_way(self, departure_date, departing_from, arriving_at):
        if (self.peak_season[0] <= departure_date and departure_date <= self.peak_season[1]):
            df = self.peak_season_flight_schedule
            df = df.loc[(df['Date'] == departure_date) & (df['Departure city'] == departing_from) & (df['Arrival city'] == arriving_at)]
            
            print(df)

            if (df.empty):
                return None, None
            
            return list(df.index), df.to_dict('records')
        
        else:
            print("loading from original server")
            return self.airlines_server.check_flight_schedule_one_way(departure_date, departing_from, arriving_at)

    def check_flight_schedule_round_trip(self, departure_date, return_date, departing_from, arriving_at):
        if (self.peak_season[0] <= departure_date and return_date <= self.peak_season[1]):
            _, out_bound_flights = self.check_flight_schedule_one_way(departure_date, departing_from, arriving_at)
            _, in_bound_flights = self.check_flight_schedule_one_way(return_date, arriving_at, departing_from)

            # 반환값 고민중..
        else:
            print("loading from original server")
            self.airlines_server.check_flight_schedule_round_trip(departure_date, return_date, departing_from, arriving_at)

    def book_flight(self, out_bound_flight_id, in_bound_flight_id, passenger_count, passengers_info, payment_method_or_agencyID):
        return self.airlines_server.book_flight(out_bound_flight_id, in_bound_flight_id, passenger_count, passengers_info, payment_method_or_agencyID)

    def cancel_flight(self, booking_reference):
        return self.airlines_server.cancle(booking_reference)

# server라는 클래스를 하나씩 두고, 각 개체를 만들까?
# 아니면 각 항공사 서버별로 클래스를 만들고, singleton pattern을 적용할까?
class AsianaAir_server:
    gen_reference_number = 0

    def __init__(self):
        self.flight_schedule = None
        self.book_list = pd.DataFrame(columns = ["Reservation date", "Booking reference", "Out_bound_flight_id", "In_bound_flight_id", "Total price", "Payment method"])
        self.peoples_list = pd.DataFrame(columns = ["Booking reference", "Name", "Gender", "Date of birth" ])

    # 엑셀 데이터를 로드해 서버내에 저장
    def import_flight_schedule_from_xlsx(self, file_path):
        self.flight_schedule = pd.read_excel(file_path)

        # [서버에 적합하게 데이터를 바꾸는 과정을 수행할 수 있음]
        # 항공사 이름 제거.
        self.flight_schedule = self.flight_schedule.drop('Airline name', axis=1)

        # Arrival time은 도착지의 시간을 기준으로 하므로, Departure time에 Flight time을 더한후 결과 값을 도착지의 시간을 기준으로 변경해야 한다.

    
    # 항공편 조회
        # 편도
            # 입력 : 가는날, 출발지, 도착지
            # 반환 : flight_id, 조회된 정보
    def check_flight_schedule_one_way(self, departure_date, departing_from, arriving_at):
        df = self.flight_schedule
        df = df.loc[(df['Date']== departure_date) & (df['Departure city'] == departing_from) & (df['Arrival city'] == arriving_at)]

        print(df)

        if (df.empty):
            return None, None

        return list(df.index), df.to_dict('records')

        # 왕복
            # 입력 : 가는날, 오는날
    def check_flight_schedule_round_trip(self, departure_date, return_date, departing_from, arriving_at):
        _, out_bound_flights = self.check_flight_schedule_one_way(departure_date, departing_from, arriving_at)
        _, in_bound_flights = self.check_flight_schedule_one_way(return_date, arriving_at, departing_from)

        # 반환값 고민중..
    # 예약
    def book_flight(self, out_bound_flight_id, in_bound_flight_id, passenger_count, passengers_info, payment_method_or_agencyID):
        # schedule_id를 토대로 서버에서 최신의 데이터를 얻어옴
        out_bound_flight = self.flight_schedule.loc[out_bound_flight_id, :]
        in_bound_flight = None
        total_price = 0

        # 승객수와 남아있는 좌석수를 비교해, 남아있는 좌석수가 크거나 같은 경우만, 예약이 가능함.
        if (out_bound_flight['Remaining seats'] < passenger_count):
            return False
        
        total_price += out_bound_flight['Price']

        if (in_bound_flight_id != None):
            in_bound_flight = self.flight_schedule.loc[in_bound_flight_id, :]

            # 승객수와 남아있는 좌석수를 비교해, 남아있는 좌석수가 크거나 같은 경우만, 예약이 가능함.
            if (in_bound_flight['Remaining seats'] < passenger_count):
                return False
            
            total_price += in_bound_flight['Price']
        
        # 예약이 가능할 경우, 승객 수 x 가격을 계산해 출력함,
        total_price = total_price * passenger_count

        # 결제 성공 여부 확인
        
        # 예약 명단 update
        now_date = "2024-07-01"
        booking_reference = self.gen_reference_number

        # [[now_date, self.gen_reference_number, out_bound_flight_id, in_bound_flight_id, total_price, payment_method_or_agencyID]], columns = ["Reservation date", "Booking reference", "Out_bound_flight_id", "In_bound_flight_id", "Total price", "Payment method"]
        new = pd.DataFrame({"Reservation date" : [now_date], "Booking reference" : [booking_reference], "Out_bound_flight_id" : [out_bound_flight_id], "In_bound_flight_id" : [in_bound_flight_id], "Total price" : [total_price], "Payment method" : [payment_method_or_agencyID]})  
        self.book_list = pd.concat([self.book_list, new], ignore_index = True)

        new = pd.DataFrame({"Booking reference" : [booking_reference for i in range(passenger_count)], "Name" : [t[0] for t in passengers_info], "Gender":[t[1] for t in passengers_info], "Date of birth":[t[2] for t in passengers_info]})
        self.peoples_list = pd.concat([self.peoples_list, new], ignore_index = True)
        
        self.gen_reference_number += 1

        # 예약 성공 여부 반환
        return True, booking_reference
    
    # 취소
    def cancel_flight(self, booking_reference):
        if (not((self.book_list["Booking reference"] == booking_reference).any())):
            return False
        
        # 중개사에서 예약한 경우, 취소할 수 없게 수정하기 바람.
        
        df = self.book_list
        df.drop(df[df["Booking reference"] == booking_reference].index, inplace = True)

        df = self.peoples_list
        df.drop(df[df["Booking reference"] == booking_reference].index, inplace = True)

        return True
    
'''
class KoreanAir_server:

class JejuAir_server:
'''


BASE_DIR = "C:\\Users\\odh30\\OneDrive\\바탕 화면\\flight_reservation_system\\data\\"

asiana_air_server = AsianaAir_server()
asiana_air_server.import_flight_schedule_from_xlsx(BASE_DIR + "asiana_air_flight_schedule (24.7.1 ~ 24.7.10).xlsx")

'''
flight_id, info = asiana_air_server.check_flight_schedule_one_way("2024-07-04", "인천(ICN)", "로마(FCO)")

asiana_air_server.check_flight_schedule_round_trip("2024-07-04", "2024-07-09", "인천(ICN)", "로마(FCO)")

passengers_info = [("Raymond", "M", "1977-05-14"), ("Emma", "W", "1999-04-19"), ("Julia", "W", "2010-12-25")]
b1, book_reference1 = asiana_air_server.book_flight(flight_id, None, 3, passengers_info, "whyparemore")

flight_id, info = asiana_air_server.check_flight_schedule_one_way("2024-07-03", "인천(ICN)", "파리(CDG)")
passengers_info = [("Billy", "M", "1974-08-17"), ("watson", "M", "1960-04-19")]
b2, book_reference2 = asiana_air_server.book_flight(flight_id, None, 2, passengers_info, "goodtrip")

b3 = asiana_air_server.cancel_flight(book_reference1)

flight_id, info = asiana_air_server.check_flight_schedule_one_way("2024-07-04", "인천(ICN)", "로마(FCO)")
passengers_info = [("Raymond", "M", "1977-05-14"), ("Emma", "W", "1999-04-19"), ("Julia", "W", "2010-12-25")]
b1, book_reference1 = asiana_air_server.book_flight(flight_id, None, 3, passengers_info, "whyparemore")
'''

# 왕복편 테스트 필요.


# 프록시 서버 테스트
proxy_server = Proxy_server(asiana_air_server)
proxy_server.add_peak_season("2024-07-02", "2024-07-05")

print(proxy_server.check_flight_schedule_one_way("2024-07-04", "인천(ICN)", "로마(FCO)"))
print(proxy_server.check_flight_schedule_one_way("2024-07-09", "로마(FCO)", "인천(ICN)"))

proxy_server.check_flight_schedule_round_trip("2024-07-04", "2024-07-05", "인천(ICN)", "로마(FCO)")


