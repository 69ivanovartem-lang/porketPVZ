using System;
using System.Collections.ObjectModel;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;

namespace WpfApp7
{
    public partial class MainWindow : Window
    {
        private ObservableCollection<Order> orders;

        public MainWindow()
        {
            InitializeComponent();
            orders = new ObservableCollection<Order>();

            // Инициализация DataGrid
            dgOrders.ItemsSource = orders;

            // Загрузка тестовых данных
            LoadSampleData();

            // Подписка на события
            btnAddOrder.Click += BtnAddOrder_Click;
            btnMenuOrders.Click += BtnMenuOrders_Click;
            btnMenuStorage.Click += BtnMenuStorage_Click;
            btnMenuCustomers.Click += BtnMenuCustomers_Click;
        }

        private void LoadSampleData()
        {
            orders.Add(new Order
            {
                OrderNumber = "ORD-2024-001",
                CustomerName = "Иванов Иван Петрович",
                Phone = "+7 (999) 123-45-67",
                Status = "Ожидает",
                CreatedDate = DateTime.Now.AddHours(-2),
                TotalAmount = 34999.99m,
                ItemsSummary = "Смартфон Samsung A54"
            });

            orders.Add(new Order
            {
                OrderNumber = "ORD-2024-002",
                CustomerName = "Петрова Анна Сергеевна",
                Phone = "+7 (999) 987-65-43",
                Status = "В пути",
                CreatedDate = DateTime.Now.AddDays(-1),
                TotalAmount = 75999.50m,
                ItemsSummary = "Ноутбук Lenovo IdeaPad"
            });

            orders.Add(new Order
            {
                OrderNumber = "ORD-2024-003",
                CustomerName = "Сидоров Петр Александрович",
                Phone = "+7 (999) 555-44-33",
                Status = "Доставлен",
                CreatedDate = DateTime.Now.AddDays(-2),
                TotalAmount = 12499.00m,
                ItemsSummary = "Наушники Sony"
            });
        }

        private void BtnAddOrder_Click(object sender, RoutedEventArgs e)
        {
            var newOrder = new Order
            {
                OrderNumber = $"ORD-{DateTime.Now:yyyyMMdd}-{(orders.Count + 1):D3}",
                CustomerName = "Новый клиент",
                Phone = "+7 (999) 000-00-00",
                Status = "Ожидает",
                CreatedDate = DateTime.Now,
                TotalAmount = 0,
                ItemsSummary = "Товары не указаны"
            };

            orders.Add(newOrder);

            MessageBox.Show($"Заказ {newOrder.OrderNumber} создан!",
                "Новый заказ",
                MessageBoxButton.OK,
                MessageBoxImage.Information);
        }

        private void BtnMenuOrders_Click(object sender, RoutedEventArgs e)
        {
            ResetMenuButtons();
            btnMenuOrders.Background = new SolidColorBrush(Color.FromRgb(33, 150, 243));
            btnMenuOrders.Foreground = new SolidColorBrush(Colors.White);
        }

        private void BtnMenuStorage_Click(object sender, RoutedEventArgs e)
        {
            ResetMenuButtons();
            btnMenuStorage.Background = new SolidColorBrush(Color.FromRgb(33, 150, 243));
            btnMenuStorage.Foreground = new SolidColorBrush(Colors.White);

            MessageBox.Show("Раздел 'Склад' находится в разработке",
                "Информация",
                MessageBoxButton.OK,
                MessageBoxImage.Information);
        }

        private void BtnMenuCustomers_Click(object sender, RoutedEventArgs e)
        {
            ResetMenuButtons();
            btnMenuCustomers.Background = new SolidColorBrush(Color.FromRgb(33, 150, 243));
            btnMenuCustomers.Foreground = new SolidColorBrush(Colors.White);

            MessageBox.Show("Раздел 'Клиенты' находится в разработке",
                "Информация",
                MessageBoxButton.OK,
                MessageBoxImage.Information);
        }

        private void ResetMenuButtons()
        {
            var transparentBrush = new SolidColorBrush(Colors.Transparent);
            var blackBrush = new SolidColorBrush(Colors.Black);

            btnMenuOrders.Background = transparentBrush;
            btnMenuOrders.Foreground = blackBrush;
            btnMenuStorage.Background = transparentBrush;
            btnMenuStorage.Foreground = blackBrush;
            btnMenuCustomers.Background = transparentBrush;
            btnMenuCustomers.Foreground = blackBrush;
        }
    }

    // КЛАСС ДАННЫХ
    public class Order
    {
        public string OrderNumber { get; set; }
        public string CustomerName { get; set; }
        public string Phone { get; set; }
        public string Status { get; set; }
        public DateTime CreatedDate { get; set; }
        public decimal TotalAmount { get; set; }
        public string ItemsSummary { get; set; }

        public Order()
        {
            OrderNumber = string.Empty;
            CustomerName = string.Empty;
            Phone = string.Empty;
            Status = string.Empty;
            CreatedDate = DateTime.Now;
            TotalAmount = 0;
            ItemsSummary = string.Empty;
        }
    }
}