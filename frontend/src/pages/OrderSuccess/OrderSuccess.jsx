import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './OrderSuccess.css';

export default function OrderSuccess() {
  const navigate = useNavigate();
  const location = useLocation();
  const { orderId, transactionId } = location.state || {};

  useEffect(() => {
    if (!orderId) {
      navigate('/');
    }
  }, [orderId, navigate]);

  return (
    <div className="order-success">
      <div className="success-container">
        <div className="success-icon">
          <svg viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="45" fill="#4ecca3" />
            <path d="M30 50 L45 65 L70 35" stroke="white" strokeWidth="8" fill="none" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </div>

        <h1>Order Placed Successfully!</h1>
        <p className="success-message">
          Thank you for your purchase. Your order has been confirmed and is being processed.
        </p>

        <div className="order-details-box">
          <div className="detail-row">
            <span className="label">Order ID:</span>
            <span className="value">#{orderId}</span>
          </div>
          {transactionId && (
            <div className="detail-row">
              <span className="label">Transaction ID:</span>
              <span className="value transaction">{transactionId}</span>
            </div>
          )}
        </div>

        <div className="success-info">
          <div className="info-item">
            <span className="icon">📧</span>
            <p>A confirmation email has been sent to your registered email address</p>
          </div>
          <div className="info-item">
            <span className="icon">📦</span>
            <p>You can track your order status in the "My Orders" section</p>
          </div>
          <div className="info-item">
            <span className="icon">🚚</span>
            <p>Expected delivery: 3-5 business days</p>
          </div>
        </div>

        <div className="success-actions">
          <button 
            className="view-orders-btn"
            onClick={() => navigate('/orders')}
          >
            View My Orders
          </button>
          <button 
            className="continue-shopping-btn"
            onClick={() => navigate('/products')}
          >
            Continue Shopping
          </button>
        </div>
      </div>
    </div>
  );
}
