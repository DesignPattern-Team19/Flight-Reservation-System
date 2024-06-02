from abc import ABCMeta, abstractmethod
import pandas as pd
import os

# 인터페이스니 무시해도 됨.
class server(metaclass = ABCMeta):
    @abstractmethod
    def query_flight_schedule_one_way(self, departure_date, departing_from, arriving_at, passengers_count):
        pass

    @abstractmethod
    def query_flight_schedule_round_trip(self, departure_date, return_date, departing_from, arriving_at, passengers_count):
        pass

    @abstractmethod
    def book_flight(self, out_bound_flight_id, in_bound_flight_id, passenger_count, passengers_info, payment_method_or_agencyID):
        pass

    @abstractmethod
    def check_reservation(self, booking_reference):
        pass

    @abstractmethod
    def cancel_flight(self, booking_reference):
        pass
    
# 클라이언트와 항공사 서버 중간에 위치하는 프록시 서버.
# 클라이언트는 항공사 서버가 아닌 프록시 서버와 통신한다.
# 프록시 서버를 둔 이유 : 성수기(peak_season)을 조회할 시 항공사 서버까지 갈 필요 없이 프록시 서버에서 조회
class Proxy_server(server):

    # 프록시 서버의 생성자
    # 입력 : 항공사 서버
    # 반환 : 반환값 없음
    def __init__(self, server):
        self.airlines_server = server
        self.peak_season = None
        self.peak_season_flight_schedule = None

    # 성수기(peak_season) 기간 설정 함수
    # 입력 : 성수기(peak_season)
    # 반환 : 없음
    # 주의 사항 : 프록시 서버로부터 항공편을 조회하기 전에 반드시 이 함수를 통해 peak_season을 정하여야 함
    def add_peak_season(self, start_date, end_date):
        df = self.airlines_server.flight_schedule
        
        self.peak_season = (start_date, end_date)
        self.peak_season_flight_schedule = df[(start_date <= df['Date']) & (df['Date'] <= end_date)]

    # 편도편 조회 함수
    # 입력 : "departure_date" = 출발일, "departing_from" = 출발지, "arriving_at" : 도착지
    # 반환 : ([항공편 id, 항공편 id, ...], [{조회된 항공편 정보}, {조회된 항공편 정보}])
    # 반환 값은 리스트 2개로 구성된 tuple이며, 첫번째 리스트는 항공편 id들을 가지고, 두번째 리스트는 조회된 항공편 정보를 dict형태로 가지고 있다.
    # 반환 값으로 받은 조회된 항공편 정보를 보기 쉽게 dataframe으로 바꾸는 방법은 아래 테스트 코드를 참조하길 바란다.
    def query_flight_schedule_one_way(self, departure_date, departing_from, arriving_at, passengers_count):
        if (self.peak_season[0] <= departure_date and departure_date <= self.peak_season[1]):
            df = self.peak_season_flight_schedule
            df = df.loc[(df['Date'] == departure_date) & (df['Departure city'] == departing_from) & (df['Arrival city'] == arriving_at) & (df["Remaining seats"] >= passengers_count)]

            if (df.empty):
                return None, None
            
            return list(df.index), df.to_dict('records')
        
        else:
            print("loading from main server")
            return self.airlines_server.query_flight_schedule_one_way(departure_date, departing_from, arriving_at, passengers_count)

    # 왕복편 조회 함수
    # 아직 이용하지 말 것.
    def query_flight_schedule_round_trip(self, departure_date, return_date, departing_from, arriving_at, passengers_count):
        if (self.peak_season[0] <= departure_date and return_date <= self.peak_season[1]):
            _, out_bound_flights = self.query_flight_schedule_one_way(departure_date, departing_from, arriving_at, passengers_count)
            _, in_bound_flights = self.query_flight_schedule_one_way(return_date, arriving_at, departing_from, passengers_count)

            # 반환값 고민중..
        else:
            print("loading from main server")
            self.airlines_server.check_flight_schedule_round_trip(departure_date, return_date, departing_from, arriving_at, passengers_count)

    # 항공편 예약 함수
    # 입력 : "out_bound_flight_id" = 가는 항공편의 id, "in_bound_flight_id" = 오는 항공편의 id, "passenger_count" = 승객 수, "passengers_info" = 승객 정보, "payment_method_or_agencyID" = 결제 수단'
    # 반환 : ( 예약 성공 여부, 예약 번호(booking_reference) ) - tuple 형태로 반환
    def book_flight(self, out_bound_flight_id, in_bound_flight_id, passenger_count, passengers_info, payment_method_or_agencyID):
        return self.airlines_server.book_flight(out_bound_flight_id, in_bound_flight_id, passenger_count, passengers_info, payment_method_or_agencyID)
    
    # 예약 조회 함수
    # 입력 : 예약 번호(booking_reference)
    # 반환 : (예약 정보, 탑승객 정보, 결제 정보) - tuple 형태로 반환
    # tuple의 각 정보는 dict형태로 제공되며, dict를 보기좋게, dataframe으로 변경하는 방법은 test 코드를 참고하라.
    def check_reservation(self, booking_reference):
        return self.airlines_server.check_reservation(booking_reference)

    # 항공편 취소 함수
    # 입력 : 예약 번호(booking_reference)
    # 반환 : 예약 취소 여부
    def cancel_flight(self, booking_reference):
        return self.airlines_server.cancel_flight(booking_reference)

# 본 서버
# 읽지 않아도 되는 클래스
class JejuAir_server:
    gen_reference_number = 0
    supported_agency = ["와이페이모어", "하나투어"]

    def __init__(self):
        self.flight_schedule = None
        self.book_list = pd.DataFrame(columns = ["Reservation date", "Booking reference", "Out_bound_flight_id", "In_bound_flight_id"])
        self.payment_info = pd.DataFrame(columns = ["Booking reference", "Payment method", "Owner name", "Card id", "Total price"]) 
        self.peoples_list = pd.DataFrame(columns = ["Booking reference", "Name", "Gender", "Date of birth" ])

    # 엑셀 데이터를 로드해 서버내에 저장
    def import_flight_schedule_from_xlsx(self, file_path):
        self.flight_schedule = pd.read_excel(file_path)

        # [서버에 적합하게 데이터를 바꾸는 과정을 수행할 수 있음]
        # 항공사 이름 제거. <- 필요없음
        # self.flight_schedule = self.flight_schedule.drop('Airline name', axis=1)

        # Arrival time은 도착지의 시간을 기준으로 하므로, Departure time에 Flight time을 더한후 결과 값을 도착지의 시간을 기준으로 변경해야 한다.

    
    # 항공편 조회
        # 편도
            # 입력 : 가는날, 출발지, 도착지
            # 반환 : flight_id, 조회된 정보
    def query_flight_schedule_one_way(self, departure_date, departing_from, arriving_at, passengers_count):
        df = self.flight_schedule
        df = df.loc[(df['Date']== departure_date) & (df['Departure city'] == departing_from) & (df['Arrival city'] == arriving_at) & (df["Remaining seats"] >= passengers_count)]

        if (df.empty):
            return None, None

        return list(df.index), df.to_dict('records')

        # 왕복
            # 입력 : 가는날, 오는날
    def query_flight_schedule_round_trip(self, departure_date, return_date, departing_from, arriving_at, passengers_count):
        _, out_bound_flights = self.query_flight_schedule_one_way(departure_date, departing_from, arriving_at, passengers_count)
        _, in_bound_flights = self.query_flight_schedule_one_way(return_date, arriving_at, departing_from, passengers_count)

        # 반환값 고민중..

    # 예약
    def book_flight(self, out_bound_flight_id, in_bound_flight_id, passenger_count, passengers_info, card_or_agencyID):
        if (out_bound_flight_id == None or len(passengers_info) != passenger_count):
            return False, None
        
        # schedule_id를 토대로 서버에서 최신의 데이터를 얻어옴
        out_bound_flight = self.flight_schedule.loc[out_bound_flight_id, :]
        in_bound_flight = None
        total_price = 0

        # 승객수와 남아있는 좌석수를 비교해, 남아있는 좌석수가 크거나 같은 경우만, 예약이 가능함.
        if (out_bound_flight['Remaining seats'] < passenger_count):
            return False, None
        
        total_price += out_bound_flight['Price(KRW)']

        if (in_bound_flight_id != None):
            in_bound_flight = self.flight_schedule.loc[in_bound_flight_id, :]

            # 승객수와 남아있는 좌석수를 비교해, 남아있는 좌석수가 크거나 같은 경우만, 예약이 가능함.
            if (in_bound_flight['Remaining seats'] < passenger_count):
                return False, None
            
            total_price += in_bound_flight['Price(KRW)']
        
        # 예약이 가능할 경우, 승객 수 x 가격을 계산해 출력함,
        total_price = total_price * passenger_count

        # 결제 성공 여부 확인
        # 임의 정보
        now_date = "2024-07-01"
        booking_reference = self.gen_reference_number

        # 결제 성공 여부 확인
        if (card_or_agencyID in self.supported_agency):
            # 대행사의 신용 결제
            new = pd.DataFrame({"Booking reference" : [booking_reference], "Payment method" : ["Agency"], "Owner name" : [card_or_agencyID], "Card id" : [None], "Total price" : [total_price]})
            self.payment_info = pd.concat([self.payment_info, new], ignore_index = True)
        else:
            try:
                card_info = card_or_agencyID.get_info()
            except:
                return False, None
            
            if (card_or_agencyID.pay(total_price)):
                new = pd.DataFrame({"Booking reference" : [booking_reference], "Payment method" : [card_info[0]], "Owner name" : [card_info[1]], "Card id" : [card_info[2]], "Total price" : [total_price]})
                self.payment_info = pd.concat([self.payment_info, new], ignore_index = True)
            else:
                return False, None

        # 예약 명단 update
        new = pd.DataFrame({"Reservation date" : [now_date], "Booking reference" : [booking_reference], "Out_bound_flight_id" : [out_bound_flight_id], "In_bound_flight_id" : [in_bound_flight_id]})  
        self.book_list = pd.concat([self.book_list, new], ignore_index = True)

        new = pd.DataFrame({"Booking reference" : [booking_reference for i in range(passenger_count)], "Name" : [t[0] for t in passengers_info], "Gender":[t[1] for t in passengers_info], "Date of birth":[t[2] for t in passengers_info]})
        self.peoples_list = pd.concat([self.peoples_list, new], ignore_index = True)
        
        self.gen_reference_number += 1

        # 예약 성공 여부 반환
        return True, booking_reference
    
    # 예약 조회
    def check_reservation(self, booking_reference):
        if (not((self.book_list["Booking reference"] == booking_reference).any())):
            return None, None, None

        df = self.book_list
        inner_reservation_info = df[df["Booking reference"] == booking_reference]
        outer_reservation_info = pd.DataFrame(columns = ["Airline name", "Reservation date", "Booking reference", "Departure city", "Arrival city", "Round trip"])
        departure_city = self.flight_schedule.iloc[inner_reservation_info["Out_bound_flight_id"]]["Departure city"].values[0]
        arrival_city = self.flight_schedule.iloc[inner_reservation_info["Out_bound_flight_id"]]["Arrival city"].values[0]

        new = pd.DataFrame({"Airline name" : ["제주 항공"], "Reservation date" : [inner_reservation_info["Reservation date"].values[0]], "Booking reference" : [booking_reference]
                             ,"Departure city" : [departure_city], "Arrival city" : [arrival_city], "Round trip":[inner_reservation_info["In_bound_flight_id"].values[0] != None]})
        
        outer_reservation_info = pd.concat([outer_reservation_info, new], ignore_index = True)

        df = self.peoples_list
        passengers_info = df[df["Booking reference"] == booking_reference]

        df = self.payment_info
        payment_info = df[df["Booking reference"] == booking_reference]

        return outer_reservation_info.to_dict('records'), passengers_info.to_dict('records'), payment_info.to_dict('records')
    
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
    

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = BASE_DIR + "\\data"

jeju_air_schedule = DATA_DIR + "\\jeju_air_flight_schedule (24.7.1 ~ 24.7.10).xlsx"

# 본 서버 생성
main_server = JejuAir_server()
main_server.import_flight_schedule_from_xlsx(jeju_air_schedule)

# 프록시 서버 테스트
proxy_server = Proxy_server(main_server)
proxy_server.add_peak_season("2024-07-02", "2024-07-05")