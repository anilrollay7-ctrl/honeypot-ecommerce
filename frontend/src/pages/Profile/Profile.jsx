import { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { updateUser } from '../../store/slices/authSlice';
import api from '../../services/api';
import './Profile.css';

export default function Profile() {
  const dispatch = useDispatch();
  const { user } = useSelector((state) => state.auth);

  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({
    name: user?.name || '',
    email: user?.email || '',
    phone: user?.phone || '',
    address: {
      street: user?.address?.street || '',
      city: user?.address?.city || '',
      state: user?.address?.state || '',
      zip: user?.address?.zip || '',
      country: user?.address?.country || ''
    }
  });

  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const response = await api.get('/auth/profile');
      const userData = response.data;
      
      setFormData({
        name: userData.name || '',
        email: userData.email || '',
        phone: userData.phone || '',
        address: userData.address || {
          street: '',
          city: '',
          state: '',
          zip: '',
          country: ''
        }
      });
    } catch (error) {
      console.error('Error fetching profile:', error);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    if (name.startsWith('address.')) {
      const addressField = name.split('.')[1];
      setFormData({
        ...formData,
        address: {
          ...formData.address,
          [addressField]: value
        }
      });
    } else {
      setFormData({ ...formData, [name]: value });
    }
  };

  const handleSave = async () => {
    setLoading(true);
    try {
      const response = await api.put('/auth/profile', formData);
      dispatch(updateUser(response.data));
      setEditing(false);
      alert('Profile updated successfully!');
    } catch (error) {
      console.error('Error updating profile:', error);
      if (error.response?.status === 401) {
        alert('Your session has expired. Please login again.');
        window.location.href = '/login';
      } else if (error.response?.data?.message) {
        alert(`Failed to update profile: ${error.response.data.message}`);
      } else {
        alert('Failed to update profile. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setFormData({
      name: user?.name || '',
      email: user?.email || '',
      phone: user?.phone || '',
      address: user?.address || {
        street: '',
        city: '',
        state: '',
        zip: '',
        country: ''
      }
    });
    setEditing(false);
  };

  return (
    <div className="profile">
      <div className="profile-container">
        <div className="profile-header">
          <h1>My Profile</h1>
          {!editing && (
            <button className="edit-btn" onClick={() => setEditing(true)}>
              ✏️ Edit Profile
            </button>
          )}
        </div>

        <div className="profile-content">
          <div className="profile-section">
            <h2>Personal Information</h2>
            <div className="profile-grid">
              <div className="profile-field">
                <label>Full Name</label>
                {editing ? (
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                  />
                ) : (
                  <p>{formData.name || 'Not provided'}</p>
                )}
              </div>

              <div className="profile-field">
                <label>Email</label>
                <p>{formData.email}</p>
                <span className="field-note">Email cannot be changed</span>
              </div>

              <div className="profile-field">
                <label>Phone</label>
                {editing ? (
                  <input
                    type="tel"
                    name="phone"
                    value={formData.phone}
                    onChange={handleInputChange}
                  />
                ) : (
                  <p>{formData.phone || 'Not provided'}</p>
                )}
              </div>
            </div>
          </div>

          <div className="profile-section">
            <h2>Shipping Address</h2>
            <div className="profile-grid">
              <div className="profile-field full-width">
                <label>Street Address</label>
                {editing ? (
                  <input
                    type="text"
                    name="address.street"
                    value={formData.address.street}
                    onChange={handleInputChange}
                  />
                ) : (
                  <p>{formData.address.street || 'Not provided'}</p>
                )}
              </div>

              <div className="profile-field">
                <label>City</label>
                {editing ? (
                  <input
                    type="text"
                    name="address.city"
                    value={formData.address.city}
                    onChange={handleInputChange}
                  />
                ) : (
                  <p>{formData.address.city || 'Not provided'}</p>
                )}
              </div>

              <div className="profile-field">
                <label>State</label>
                {editing ? (
                  <input
                    type="text"
                    name="address.state"
                    value={formData.address.state}
                    onChange={handleInputChange}
                  />
                ) : (
                  <p>{formData.address.state || 'Not provided'}</p>
                )}
              </div>

              <div className="profile-field">
                <label>ZIP Code</label>
                {editing ? (
                  <input
                    type="text"
                    name="address.zip"
                    value={formData.address.zip}
                    onChange={handleInputChange}
                  />
                ) : (
                  <p>{formData.address.zip || 'Not provided'}</p>
                )}
              </div>

              <div className="profile-field">
                <label>Country</label>
                {editing ? (
                  <input
                    type="text"
                    name="address.country"
                    value={formData.address.country}
                    onChange={handleInputChange}
                  />
                ) : (
                  <p>{formData.address.country || 'Not provided'}</p>
                )}
              </div>
            </div>
          </div>

          <div className="profile-section">
            <h2>Account Details</h2>
            <div className="profile-stats">
              <div className="stat-card">
                <div className="stat-icon">📦</div>
                <div className="stat-info">
                  <h3>Total Orders</h3>
                  <p className="stat-value">View Orders</p>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon">📅</div>
                <div className="stat-info">
                  <h3>Member Since</h3>
                  <p className="stat-value">
                    {user?.created_at 
                      ? new Date(user.created_at).toLocaleDateString() 
                      : 'N/A'}
                  </p>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon">⭐</div>
                <div className="stat-info">
                  <h3>Status</h3>
                  <p className="stat-value status-active">Active</p>
                </div>
              </div>
            </div>
          </div>

          {editing && (
            <div className="profile-actions">
              <button 
                className="save-btn" 
                onClick={handleSave}
                disabled={loading}
              >
                {loading ? 'Saving...' : '✓ Save Changes'}
              </button>
              <button 
                className="cancel-btn" 
                onClick={handleCancel}
                disabled={loading}
              >
                ✕ Cancel
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
