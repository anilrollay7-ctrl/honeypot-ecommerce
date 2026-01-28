import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';
import './Orders.css';

export default function Orders() {
  const navigate = useNavigate();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedOrder, setSelectedOrder] = useState(null);

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      const response = await api.get('/orders');
      setOrders(response.data);
    } catch (error) {
      console.error('Error fetching orders:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      confirmed: '#4ecca3',
      processing: '#ffd93d',
      shipped: '#667eea',
      delivered: '#6BCF7F',
      cancelled: '#ff6b6b'
    };
    return colors[status] || '#aaa';
  };

  const getStatusIcon = (status) => {
    const icons = {
      confirmed: '✓',
      processing: '⟳',
      shipped: '🚚',
      delivered: '📦',
      cancelled: '✕'
    };
    return icons[status] || '•';
  };

  if (loading) {
    return (
      <div className="orders-loading">
        <div className="spinner"></div>
        <p>Loading your orders...</p>
      </div>
    );
  }

  if (orders.length === 0) {
    return (
      <div className="orders-empty">
        <div className="empty-icon">📦</div>
        <h2>No Orders Yet</h2>
        <p>You haven't placed any orders yet.</p>
        <button onClick={() => navigate('/products')}>
          Start Shopping
        </button>
      </div>
    );
  }

  return (
    <div className="orders">
      <div className="orders-container">
        <div className="orders-header">
          <h1>My Orders</h1>
          <div className="orders-summary">
            <span>Total Orders: <strong>{orders.length}</strong></span>
          </div>
        </div>

        <div className="orders-list">
          {orders.map((order) => (
            <div 
              key={order.id} 
              className={`order-card ${selectedOrder?.id === order.id ? 'expanded' : ''}`}
              onClick={() => setSelectedOrder(selectedOrder?.id === order.id ? null : order)}
            >
              <div className="order-header">
                <div className="order-info">
                  <h3>Order #{order.order_id}</h3>
                  <p className="order-date">
                    {new Date(order.created_at).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}
                  </p>
                </div>

                <div className="order-status-badge" style={{ backgroundColor: getStatusColor(order.status) }}>
                  {getStatusIcon(order.status)} {order.status.toUpperCase()}
                </div>

                <div className="order-total">
                  <span className="total-label">Total</span>
                  <span className="total-amount">${order.total?.toFixed(2)}</span>
                </div>
              </div>

              {selectedOrder?.id === order.id && (
                <div className="order-details">
                  <div className="order-items">
                    <h4>Items ({order.items.length})</h4>
                    <div className="items-list">
                      {order.items.map((item, index) => (
                        <div key={index} className="order-item">
                          <img src={item.image} alt={item.name} />
                          <div className="item-info">
                            <h5>{item.name}</h5>
                            <p>Quantity: {item.quantity}</p>
                          </div>
                          <div className="item-price">
                            ${(item.price * item.quantity).toFixed(2)}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="order-info-grid">
                    <div className="info-section">
                      <h4>Shipping Address</h4>
                      <div className="address-box">
                        <p>{order.shipping_address?.fullName}</p>
                        <p>{order.shipping_address?.address}</p>
                        <p>
                          {order.shipping_address?.city}, {order.shipping_address?.state} {order.shipping_address?.zipCode}
                        </p>
                        <p>{order.shipping_address?.phone}</p>
                      </div>
                    </div>

                    <div className="info-section">
                      <h4>Payment Details</h4>
                      <div className="payment-box">
                        <p>Method: <strong>{order.payment?.method?.replace('_', ' ')}</strong></p>
                        <p>Status: <span className="payment-status">{order.payment?.status}</span></p>
                        <p>Transaction ID: <span className="transaction-id">{order.payment?.transaction_id}</span></p>
                        {order.payment?.last_four && (
                          <p>Card ending in: ****{order.payment.last_four}</p>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="order-actions">
                    <button className="track-btn">
                      📍 Track Order
                    </button>
                    <button className="invoice-btn">
                      📄 Download Invoice
                    </button>
                    <button className="help-btn">
                      💬 Get Help
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
