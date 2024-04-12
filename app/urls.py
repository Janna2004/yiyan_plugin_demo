from django.urls import path
from app.view import hotel_recommend,route_plan,day_plan

urlpatterns = [
    path("search_hotel/", hotel_recommend.hotel_recommend, name="search_hotel"),
    path("day_plan/", day_plan.day_plan, name="day_plan"),
    path("route_plan/", route_plan.route_plan, name="route_plan"),

]
