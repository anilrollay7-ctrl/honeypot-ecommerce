import React from 'react'
import { Link } from 'react-router-dom'
import { FiGithub, FiTwitter, FiFacebook, FiInstagram, FiMail, FiPhone, FiMapPin } from 'react-icons/fi'
import './Footer.css'

const Footer = () => {
  return (
    <footer className="footer">
      <div className="container footer-container">
        <div className="footer-section">
          <h3 className="footer-title">
            <span className="logo-icon">⚡</span> TechStore
          </h3>
          <p className="footer-description">
            Your one-stop shop for premium electronics, gadgets, and gaming gear. 
            Quality products at unbeatable prices.
          </p>
          <div className="social-links">
            <a href="#" className="social-icon"><FiFacebook /></a>
            <a href="#" className="social-icon"><FiTwitter /></a>
            <a href="#" className="social-icon"><FiInstagram /></a>
            <a href="#" className="social-icon"><FiGithub /></a>
          </div>
        </div>

        <div className="footer-section">
          <h4 className="footer-heading">Quick Links</h4>
          <ul className="footer-links">
            <li><Link to="/products">All Products</Link></li>
            <li><Link to="/products/electronics">Electronics</Link></li>
            <li><Link to="/products/accessories">Accessories</Link></li>
            <li><Link to="/products/gaming">Gaming</Link></li>
          </ul>
        </div>

        <div className="footer-section">
          <h4 className="footer-heading">Customer Service</h4>
          <ul className="footer-links">
            <li><Link to="/about">About Us</Link></li>
            <li><Link to="/contact">Contact Us</Link></li>
            <li><Link to="/shipping">Shipping Info</Link></li>
            <li><Link to="/returns">Returns & Refunds</Link></li>
            <li><Link to="/faq">FAQ</Link></li>
          </ul>
        </div>

        <div className="footer-section">
          <h4 className="footer-heading">Contact Info</h4>
          <ul className="contact-info">
            <li>
              <FiMapPin className="contact-icon" />
              <span>123 Tech Street, Silicon Valley, CA 94025</span>
            </li>
            <li>
              <FiPhone className="contact-icon" />
              <span>+1 (555) 123-4567</span>
            </li>
            <li>
              <FiMail className="contact-icon" />
              <span>support@techstore.com</span>
            </li>
          </ul>
        </div>
      </div>

      <div className="footer-bottom">
        <div className="container">
          <p>&copy; 2026 TechStore. All rights reserved.</p>
          <div className="footer-bottom-links">
            <Link to="/privacy">Privacy Policy</Link>
            <Link to="/terms">Terms of Service</Link>
            <Link to="/cookies">Cookie Policy</Link>
          </div>
        </div>
      </div>
    </footer>
  )
}

export default Footer
