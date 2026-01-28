import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { clearCart } from '../../store/slices/cartSlice';
import api from '../../services/api';
import './Checkout.css';

export default function Checkout() {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { items } = useSelector((state) => state.cart);
  const { user } = useSelector((state) => state.auth);

  const [shippingAddress, setShippingAddress] = useState({
    fullName: user?.name || '',
    address: '',
    city: '',
    state: '',
    zipCode: '',
    phone: user?.phone || ''
  });

  const [paymentMethod, setPaymentMethod] = useState('credit_card');
  const [paymentDetails, setPaymentDetails] = useState({
    cardNumber: '',
    cardName: '',
    expiryDate: '',
    cvv: ''
  });

  const [processing, setProcessing] = useState(false);

  const subtotal = items.reduce((sum, item) => {
    const price = item.discount 
      ? item.price * (1 - item.discount / 100) 
      : item.price;
    return sum + price * item.quantity;
  }, 0);

  const shipping = subtotal > 100 ? 0 : 15;
  const tax = subtotal * 0.1;
  const total = subtotal + shipping + tax;

  const handleInputChange = (e, section) => {
    const { name, value } = e.target;
    if (section === 'shipping') {
      setShippingAddress({ ...shippingAddress, [name]: value });
    } else if (section === 'payment') {
      setPaymentDetails({ ...paymentDetails, [name]: value });
    }
  };

  const handlePlaceOrder = async () => {
    // Validate shipping address
    if (!shippingAddress.fullName || !shippingAddress.address || 
        !shippingAddress.city || !shippingAddress.phone) {
      alert('Please fill in all shipping details');
      return;
    }

    // Validate payment details
    if (paymentMethod === 'credit_card' || paymentMethod === 'debit_card') {
      if (!paymentDetails.cardNumber || !paymentDetails.cardName || 
          !paymentDetails.expiryDate || !paymentDetails.cvv) {
        alert('Please fill in all payment details');
        return;
      }
    }

    setProcessing(true);

    try {
      // Simulate payment processing
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Create order
      const orderData = {
        items: items.map(item => ({
          id: item.id,
          name: item.name,
          price: item.discount 
            ? item.price * (1 - item.discount / 100) 
            : item.price,
          quantity: item.quantity,
          image: item.image
        })),
        shippingAddress: {
          street: shippingAddress.address,
          city: shippingAddress.city,
          state: shippingAddress.state,
          zip: shippingAddress.zipCode,
          country: 'USA',
          fullName: shippingAddress.fullName,
          phone: shippingAddress.phone
        },
        paymentDetails: {
          method: paymentMethod,
          last_four: paymentDetails.cardNumber ? paymentDetails.cardNumber.slice(-4) : '0000',
          cardName: paymentDetails.cardName
        }
      };

      const response = await api.post('/orders', orderData);

      // Clear cart
      dispatch(clearCart());

      // Redirect to success page
      navigate('/order-success', { 
        state: { 
          orderId: response.data.order_id,
          transactionId: response.data.transaction_id
        } 
      });
    } catch (error) {
      console.error('Error placing order:', error);
      if (error.response?.status === 401) {
        alert('Your session has expired. Please login again.');
        navigate('/login');
      } else if (error.response?.data?.message) {
        alert(`Payment failed: ${error.response.data.message}`);
      } else {
        alert('Payment failed! Please try again.');
      }
    } finally {
      setProcessing(false);
    }
  };

  if (items.length === 0) {
    return (
      <div className="checkout-empty">
        <h2>Your cart is empty</h2>
        <button onClick={() => navigate('/products')}>Continue Shopping</button>
      </div>
    );
  }

  return (
    <div className="checkout">
      <div className="checkout-container">
        <h1>Checkout</h1>

        <div className="checkout-grid">
          <div className="checkout-forms">
            {/* Shipping Address */}
            <div className="checkout-section">
              <h2>Shipping Address</h2>
              <div className="form-grid">
                <input
                  type="text"
                  name="fullName"
                  placeholder="Full Name"
                  value={shippingAddress.fullName}
                  onChange={(e) => handleInputChange(e, 'shipping')}
                  required
                />
                <input
                  type="tel"
                  name="phone"
                  placeholder="Phone Number"
                  value={shippingAddress.phone}
                  onChange={(e) => handleInputChange(e, 'shipping')}
                  required
                />
                <input
                  type="text"
                  name="address"
                  placeholder="Street Address"
                  className="full-width"
                  value={shippingAddress.address}
                  onChange={(e) => handleInputChange(e, 'shipping')}
                  required
                />
                <input
                  type="text"
                  name="city"
                  placeholder="City"
                  value={shippingAddress.city}
                  onChange={(e) => handleInputChange(e, 'shipping')}
                  required
                />
                <input
                  type="text"
                  name="state"
                  placeholder="State"
                  value={shippingAddress.state}
                  onChange={(e) => handleInputChange(e, 'shipping')}
                />
                <input
                  type="text"
                  name="zipCode"
                  placeholder="ZIP Code"
                  value={shippingAddress.zipCode}
                  onChange={(e) => handleInputChange(e, 'shipping')}
                />
              </div>
            </div>

            {/* Payment Method */}
            <div className="checkout-section">
              <h2>Payment Method</h2>
              <div className="payment-methods">
                <label className={paymentMethod === 'credit_card' ? 'active' : ''}>
                  <input
                    type="radio"
                    name="paymentMethod"
                    value="credit_card"
                    checked={paymentMethod === 'credit_card'}
                    onChange={(e) => setPaymentMethod(e.target.value)}
                  />
                  <span>💳 Credit Card</span>
                </label>
                <label className={paymentMethod === 'debit_card' ? 'active' : ''}>
                  <input
                    type="radio"
                    name="paymentMethod"
                    value="debit_card"
                    checked={paymentMethod === 'debit_card'}
                    onChange={(e) => setPaymentMethod(e.target.value)}
                  />
                  <span>💳 Debit Card</span>
                </label>
                <label className={paymentMethod === 'paypal' ? 'active' : ''}>
                  <input
                    type="radio"
                    name="paymentMethod"
                    value="paypal"
                    checked={paymentMethod === 'paypal'}
                    onChange={(e) => setPaymentMethod(e.target.value)}
                  />
                  <span>🅿️ PayPal</span>
                </label>
                <label className={paymentMethod === 'cash_on_delivery' ? 'active' : ''}>
                  <input
                    type="radio"
                    name="paymentMethod"
                    value="cash_on_delivery"
                    checked={paymentMethod === 'cash_on_delivery'}
                    onChange={(e) => setPaymentMethod(e.target.value)}
                  />
                  <span>💵 Cash on Delivery</span>
                </label>
              </div>

              {(paymentMethod === 'credit_card' || paymentMethod === 'debit_card') && (
                <div className="card-details">
                  <input
                    type="text"
                    name="cardNumber"
                    placeholder="Card Number (e.g., 4111 1111 1111 1111)"
                    value={paymentDetails.cardNumber}
                    onChange={(e) => handleInputChange(e, 'payment')}
                    maxLength="19"
                  />
                  <input
                    type="text"
                    name="cardName"
                    placeholder="Cardholder Name"
                    value={paymentDetails.cardName}
                    onChange={(e) => handleInputChange(e, 'payment')}
                  />
                  <div className="card-row">
                    <input
                      type="text"
                      name="expiryDate"
                      placeholder="MM/YY"
                      value={paymentDetails.expiryDate}
                      onChange={(e) => handleInputChange(e, 'payment')}
                      maxLength="5"
                    />
                    <input
                      type="text"
                      name="cvv"
                      placeholder="CVV"
                      value={paymentDetails.cvv}
                      onChange={(e) => handleInputChange(e, 'payment')}
                      maxLength="4"
                    />
                  </div>
                  <p className="dummy-note">
                    💡 This is a demo. Use any card number (e.g., 4111 1111 1111 1111)
                  </p>
                </div>
              )}

              {paymentMethod === 'paypal' && (
                <div className="paypal-info">
                  <p>You will be redirected to PayPal to complete your purchase.</p>
                  <p className="dummy-note">💡 This is a demo. PayPal payment will be simulated.</p>
                </div>
              )}

              {paymentMethod === 'cash_on_delivery' && (
                <div className="cod-info">
                  <p>Pay with cash when your order is delivered.</p>
                  <p>An additional fee of $5 may apply.</p>
                </div>
              )}
            </div>
          </div>

          {/* Order Summary */}
          <div className="order-summary">
            <h2>Order Summary</h2>
            
            <div className="summary-items">
              {items.map((item) => {
                const price = item.discount 
                  ? item.price * (1 - item.discount / 100) 
                  : item.price;
                
                return (
                  <div key={item.id} className="summary-item">
                    <img src={item.image} alt={item.name} />
                    <div className="item-details">
                      <h4>{item.name}</h4>
                      <p>Qty: {item.quantity}</p>
                    </div>
                    <div className="item-price">
                      ${(price * item.quantity).toFixed(2)}
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="summary-totals">
              <div className="total-row">
                <span>Subtotal</span>
                <span>${subtotal.toFixed(2)}</span>
              </div>
              <div className="total-row">
                <span>Shipping</span>
                <span>{shipping === 0 ? 'FREE' : `$${shipping.toFixed(2)}`}</span>
              </div>
              <div className="total-row">
                <span>Tax (10%)</span>
                <span>${tax.toFixed(2)}</span>
              </div>
              <div className="total-row total">
                <span>Total</span>
                <span>${total.toFixed(2)}</span>
              </div>
            </div>

            <button 
              className="place-order-btn"
              onClick={handlePlaceOrder}
              disabled={processing}
            >
              {processing ? 'Processing Payment...' : 'Place Order'}
            </button>

            <div className="security-badges">
              <div className="badge">🔒 Secure Checkout</div>
              <div className="badge">✓ Money-back Guarantee</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
