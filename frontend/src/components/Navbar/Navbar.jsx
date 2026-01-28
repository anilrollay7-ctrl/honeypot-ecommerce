import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useSelector, useDispatch } from 'react-redux'
import { FiShoppingCart, FiUser, FiSearch, FiMenu, FiX, FiLogOut } from 'react-icons/fi'
import { logout } from '../../store/slices/authSlice'
import './Navbar.css'

const Navbar = () => {
  const navigate = useNavigate()
  const dispatch = useDispatch()
  const { isAuthenticated, user } = useSelector((state) => state.auth)
  const { itemCount } = useSelector((state) => state.cart)
  const [searchQuery, setSearchQuery] = useState('')
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const handleSearch = (e) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      navigate(`/products?search=${searchQuery}`)
      setSearchQuery('')
    }
  }

  const handleLogout = () => {
    dispatch(logout())
    navigate('/')
  }

  return (
    <nav className="navbar">
      <div className="container navbar-container">
        <Link to="/" className="logo">
          <span className="logo-icon">⚡</span>
          <span className="logo-text">TechStore</span>
        </Link>

        <form className="search-bar" onSubmit={handleSearch}>
          <FiSearch className="search-icon" />
          <input
            type="text"
            placeholder="Search products..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <button type="submit">Search</button>
        </form>

        <div className="nav-links">
          <Link to="/products" className="nav-link">Products</Link>
          <Link to="/products/electronics" className="nav-link">Electronics</Link>
          <Link to="/products/accessories" className="nav-link">Accessories</Link>
          <Link to="/products/gaming" className="nav-link">Gaming</Link>
        </div>

        <div className="nav-actions">
          <Link to="/cart" className="icon-button">
            <FiShoppingCart />
            {itemCount > 0 && <span className="badge">{itemCount}</span>}
          </Link>

          {isAuthenticated ? (
            <div className="user-menu">
              <button className="icon-button user-button">
                <FiUser />
                <span>{user?.name || 'User'}</span>
              </button>
              <div className="dropdown-menu">
                <Link to="/profile" className="dropdown-item">Profile</Link>
                <Link to="/orders" className="dropdown-item">My Orders</Link>
                <button onClick={handleLogout} className="dropdown-item">
                  <FiLogOut /> Logout
                </button>
              </div>
            </div>
          ) : (
            <Link to="/login" className="btn-primary">Login</Link>
          )}

          <button className="mobile-menu-toggle" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
            {mobileMenuOpen ? <FiX /> : <FiMenu />}
          </button>
        </div>
      </div>

      {mobileMenuOpen && (
        <div className="mobile-menu">
          <Link to="/products" onClick={() => setMobileMenuOpen(false)}>Products</Link>
          <Link to="/products/electronics" onClick={() => setMobileMenuOpen(false)}>Electronics</Link>
          <Link to="/products/accessories" onClick={() => setMobileMenuOpen(false)}>Accessories</Link>
          <Link to="/products/gaming" onClick={() => setMobileMenuOpen(false)}>Gaming</Link>
        </div>
      )}
    </nav>
  )
}

export default Navbar
