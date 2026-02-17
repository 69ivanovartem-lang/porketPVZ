using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;

namespace PVZApp
{
    public partial class MainWindow : Window
    {
        private ObservableCollection<Order> _allOrders;
        private ICollectionView _ordersView;

        public MainWindow()
        {
            InitializeComponent();
            LoadSampleData();
            SetupFiltering();
        }

        private void LoadSampleData()
        {
            _allOrders = new ObservableCollection<Order>
            {
                new Order
                {
                    OrderNumber = "ORD-001",
                    OrderDate = DateTime.Now.AddDays(-2),
                    ClientName = "Иванов Иван Иванович",
                    Phone = "+7 (999) 123-45-67",
                    Status = "Готов к выдаче",
                    Amount = 3450.50m,
                    DeliveryMethod = "Самовывоз",
                    PickupPoint = "ПВЗ №001"
                },
                new Order
                {
                    OrderNumber = "ORD-002",
                    OrderDate = DateTime.Now.AddDays(-1),
                    ClientName = "Петрова Анна Сергеевна",
                    Phone = "+7 (999) 765-43-21",
                    Status = "Ожидает выдачи",
                    Amount = 8900.00m,
                    DeliveryMethod = "Курьер",
                    PickupPoint = "ПВЗ №001"
                },
                new Order
                {
                    OrderNumber = "ORD-003",
                    OrderDate = DateTime.Now,
                    ClientName = "Сидоров Алексей Петрович",
                    Phone = "+7 (999) 555-66-77",
                    Status = "Выдан",
                    Amount = 2300.00m,
                    DeliveryMethod = "Самовывоз",
                    PickupPoint = "ПВЗ №001"
                },
                new Order
                {
                    OrderNumber = "ORD-004",
                    OrderDate = DateTime.Now.AddDays(-3),
                    ClientName = "Козлова Елена Владимировна",
                    Phone = "+7 (999) 111-22-33",
                    Status = "Отменен",
                    Amount = 5600.00m,
                    DeliveryMethod = "Самовывоз",
                    PickupPoint = "ПВЗ №001"
                },
                new Order
                {
                    OrderNumber = "ORD-005",
                    OrderDate = DateTime.Now.AddDays(-1),
                    ClientName = "Николаев Дмитрий Сергеевич",
                    Phone = "+7 (999) 444-55-66",
                    Status = "Готов к выдаче",
                    Amount = 12500.00m,
                    DeliveryMethod = "Курьер",
                    PickupPoint = "ПВЗ №001"
                },
                new Order
                {
                    OrderNumber = "ORD-006",
                    OrderDate = DateTime.Now,
                    ClientName = "Соколова Мария Андреевна",
                    Phone = "+7 (999) 777-88-99",
                    Status = "Ожидает выдачи",
                    Amount = 4300.50m,
                    DeliveryMethod = "Самовывоз",
                    PickupPoint = "ПВЗ №001"
                }
            };

            OrdersDataGrid.ItemsSource = _allOrders;
        }

        private void SetupFiltering()
        {
            _ordersView = CollectionViewSource.GetDefaultView(_allOrders);
            _ordersView.Filter = FilterOrders;
        }

        private bool FilterOrders(object item)
        {
            if (string.IsNullOrWhiteSpace(SearchBox.Text))
                return true;

            var order = item as Order;
            if (order == null)
                return false;

            string searchText = SearchBox.Text.ToLower();
            return order.OrderNumber.ToLower().Contains(searchText) ||
                   order.ClientName.ToLower().Contains(searchText) ||
                   order.Phone.Contains(searchText);
        }

        private void SearchBox_TextChanged(object sender, TextChangedEventArgs e)
        {
            _ordersView?.Refresh();
        }

        private void SearchButton_Click(object sender, RoutedEventArgs e)
        {
            _ordersView?.Refresh();
        }

        private void RefreshButton_Click(object sender, RoutedEventArgs e)
        {
            SearchBox.Text = string.Empty;
            _ordersView?.Refresh();
            OrdersDataGrid.SelectedItem = null;
            UpdateSelectedOrderInfo(null);
        }

        private void OrdersDataGrid_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            var selectedOrder = OrdersDataGrid.SelectedItem as Order;
            UpdateSelectedOrderInfo(selectedOrder);
        }

        private void UpdateSelectedOrderInfo(Order order)
        {
            if (order != null)
            {
                SelectedOrderNumber.Text = order.OrderNumber;
                OrderDetails.Text = order.GetDetails();
                IssueButton.IsEnabled = order.Status != "Выдан" && order.Status != "Отменен";
                CancelButton.IsEnabled = order.Status != "Выдан" && order.Status != "Отменен";
            }
            else
            {
                SelectedOrderNumber.Text = "-";
                OrderDetails.Text = "Выберите заказ для просмотра деталей";
                IssueButton.IsEnabled = false;
                CancelButton.IsEnabled = false;
            }
        }

        private void IssueButton_Click(object sender, RoutedEventArgs e)
        {
            var selectedOrder = OrdersDataGrid.SelectedItem as Order;
            if (selectedOrder != null)
            {
                var result = MessageBox.Show($"Выдать заказ {selectedOrder.OrderNumber} клиенту {selectedOrder.ClientName}?",
                    "Подтверждение выдачи", MessageBoxButton.YesNo, MessageBoxImage.Question);

                if (result == MessageBoxResult.Yes)
                {
                    selectedOrder.Status = "Выдан";
                    OrdersDataGrid.Items.Refresh();
                    UpdateSelectedOrderInfo(selectedOrder);
                    MessageBox.Show("Заказ успешно выдан!", "Информация", MessageBoxButton.OK, MessageBoxImage.Information);
                }
            }
        }

        private void CancelButton_Click(object sender, RoutedEventArgs e)
        {
            var selectedOrder = OrdersDataGrid.SelectedItem as Order;
            if (selectedOrder != null)
            {
                var result = MessageBox.Show($"Отменить заказ {selectedOrder.OrderNumber}?",
                    "Подтверждение отмены", MessageBoxButton.YesNo, MessageBoxImage.Warning);

                if (result == MessageBoxResult.Yes)
                {
                    selectedOrder.Status = "Отменен";
                    OrdersDataGrid.Items.Refresh();
                    UpdateSelectedOrderInfo(selectedOrder);
                    MessageBox.Show("Заказ отменен!", "Информация", MessageBoxButton.OK, MessageBoxImage.Information);
                }
            }
        }

        private void AddOrderButton_Click(object sender, RoutedEventArgs e)
        {
            // Здесь можно открыть окно добавления нового заказа
            MessageBox.Show("Функция добавления заказа будет доступна в следующей версии",
                "Информация", MessageBoxButton.OK, MessageBoxImage.Information);
        }
    }
}