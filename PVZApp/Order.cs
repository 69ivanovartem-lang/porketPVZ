using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PVZApp
{
    public class Order
    {
        public string OrderNumber { get; set; }
        public DateTime OrderDate { get; set; }
        public string ClientName { get; set; }
        public string Phone { get; set; }
        public string Status { get; set; }
        public decimal Amount { get; set; }
        public string DeliveryMethod { get; set; }
        public string PickupPoint { get; set; }

        // Цвет статуса для отображения
        public string StatusColor
        {
            get
            {
                switch (Status)
                {
                    case "Ожидает выдачи":
                        return "#F39C12"; // Оранжевый
                    case "Выдан":
                        return "#27AE60"; // Зеленый
                    case "Отменен":
                        return "#E74C3C"; // Красный
                    case "Готов к выдаче":
                        return "#3498DB"; // Синий
                    default:
                        return "#95A5A6"; // Серый
                }
            }
        }

        // Детальная информация о заказе
        public string GetDetails()
        {
            return $"Заказ {OrderNumber} от {OrderDate:dd.MM.yyyy}\n" +
                   $"Клиент: {ClientName}, тел: {Phone}\n" +
                   $"Сумма: {Amount:C}\n" +
                   $"Способ получения: {DeliveryMethod}\n" +
                   $"Пункт выдачи: {PickupPoint}\n" +
                   $"Статус: {Status}";
        }
    }
}