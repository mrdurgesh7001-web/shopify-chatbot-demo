import streamlit as st
import json
from datetime import datetime, timedelta
import random

# ============================================
# SHOPIFY INTEGRATION (Optional - Enable when client ready)
# ============================================

# Set to True when connecting to real Shopify store
USE_REAL_SHOPIFY = False  # ← Change to True for real integration

if USE_REAL_SHOPIFY:
    try:
        import shopify
        SHOPIFY_AVAILABLE = True
    except ImportError:
        SHOPIFY_AVAILABLE = False
        st.warning("⚠️ Shopify library not installed. Run: pip install shopify-python-api")
else:
    SHOPIFY_AVAILABLE = False

# ============================================
# SHOPIFY CONFIGURATION
# ============================================

SHOPIFY_CONFIG = {
    "shop_url": "client-store.myshopify.com",  # Client provides this
    "api_key": "client_api_key_here",          # Client provides this
    "api_password": "client_api_password_here" # Client provides this
}

def connect_to_shopify(shop_url, api_key, api_password):
    """Connect to client's Shopify store"""
    if not SHOPIFY_AVAILABLE:
        return False
    
    try:
        shop_url = f"https://{api_key}:{api_password}@{shop_url}/admin/api/2024-01"
        shopify.ShopifyResource.set_site(shop_url)
        return True
    except Exception as e:
        st.error(f"Shopify connection failed: {e}")
        return False

# Connect to Shopify if enabled
if USE_REAL_SHOPIFY and SHOPIFY_AVAILABLE:
    shopify_connected = connect_to_shopify(
        SHOPIFY_CONFIG['shop_url'],
        SHOPIFY_CONFIG['api_key'],
        SHOPIFY_CONFIG['api_password']
    )
    if shopify_connected:
        st.sidebar.success("✅ Connected to Shopify!")
else:
    shopify_connected = False

# ============================================
# Page Configuration
# ============================================

st.set_page_config(
    page_title="AI Shopping Assistant",
    page_icon="🛍️",
    layout="centered"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #f5f5f5;
    }
    .stTextInput>div>div>input {
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# STORE CONFIGURATION
# ============================================

STORE_CONFIG = {
    "name": "StyleHub",
    "products": "Fashion, Shoes, Accessories",
    "free_shipping": 50,
    "delivery_days": "3-5",
    "return_days": 30,
    "email": "support@stylehub.com",
    "phone": "+1-800-STYLE",
    "currency": "$"
}

# ============================================
# SAMPLE PRODUCTS DATABASE (Demo Mode)
# ============================================

PRODUCTS = [
    {
        "id": 1,
        "name": "Classic Denim Jacket",
        "price": 89.99,
        "category": "Outerwear",
        "rating": 4.5,
        "stock": 15,
        "image": "🧥"
    },
    {
        "id": 2,
        "name": "White Sneakers",
        "price": 79.99,
        "category": "Shoes",
        "rating": 4.8,
        "stock": 8,
        "image": "👟"
    },
    {
        "id": 3,
        "name": "Summer Floral Dress",
        "price": 69.99,
        "category": "Dresses",
        "rating": 4.7,
        "stock": 20,
        "image": "👗"
    },
    {
        "id": 4,
        "name": "Leather Crossbody Bag",
        "price": 129.99,
        "category": "Accessories",
        "rating": 4.9,
        "stock": 12,
        "image": "👜"
    },
    {
        "id": 5,
        "name": "Slim Fit Black Jeans",
        "price": 59.99,
        "category": "Bottoms",
        "rating": 4.6,
        "stock": 25,
        "image": "👖"
    }
]

# ============================================
# SAMPLE ORDERS (Demo Mode)
# ============================================

SAMPLE_ORDERS = {
    "12345": {
        "order_number": "12345",
        "status": "In Transit",
        "items": ["White Sneakers", "Classic Denim Jacket"],
        "total": 169.98,
        "tracking": "TRK789456123",
        "estimated_delivery": (datetime.now() + timedelta(days=2)).strftime("%B %d, %Y"),
        "can_cancel": False,
        "can_return": False
    },
    "67890": {
        "order_number": "67890",
        "status": "Processing",
        "items": ["Summer Floral Dress"],
        "total": 69.99,
        "tracking": "Processing",
        "estimated_delivery": (datetime.now() + timedelta(days=5)).strftime("%B %d, %Y"),
        "can_cancel": True,
        "can_return": False
    },
    "54321": {
        "order_number": "54321",
        "status": "Delivered",
        "items": ["Leather Crossbody Bag"],
        "total": 129.99,
        "tracking": "DELIVERED",
        "estimated_delivery": "Delivered on " + (datetime.now() - timedelta(days=3)).strftime("%B %d, %Y"),
        "can_cancel": False,
        "can_return": True
    }
}

# ============================================
# FAQ DATABASE
# ============================================

FAQ_DATABASE = {
    "shipping_time": f"Standard shipping takes {STORE_CONFIG['delivery_days']} business days.",
    "free_shipping": f"Yes! Free shipping on all orders over ${STORE_CONFIG['free_shipping']}.",
    "returns": f"We offer {STORE_CONFIG['return_days']}-day free returns on all items.",
}

# ============================================
# SESSION STATE INITIALIZATION
# ============================================

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": f"Hello! 👋 Welcome to {STORE_CONFIG['name']}! I'm your AI shopping assistant.\n\n**I can help you with:**\n\n🔍 Product recommendations\n📦 Order tracking\n🔄 Returns & exchanges\n💳 Payment & shipping info\n📧 Exclusive deals\n\nWhat would you like to know?"
        }
    ]

if "user_email" not in st.session_state:
    st.session_state.user_email = None

if "user_name" not in st.session_state:
    st.session_state.user_name = None

# ============================================
# REAL SHOPIFY FUNCTIONS
# ============================================

def track_order_real(order_number):
    """Track REAL Shopify order"""
    if not shopify_connected:
        return "❌ Shopify integration not configured. Contact administrator."
    
    try:
        orders = shopify.Order.find(name=f"#{order_number}")
        
        if not orders:
            return f"❌ Order #{order_number} not found in the system."
        
        order = orders[0]
        
        response = f"""
📦 **Order Tracking - #{order.order_number}**

**Customer:** {order.customer.first_name} {order.customer.last_name}
**Email:** {order.email}

**Status:** {order.financial_status.upper()} ✅

**Items Ordered:**
"""
        
        for item in order.line_items:
            response += f"\n• {item.name} (Qty: {item.quantity}) - ${item.price}"
        
        response += f"""

**Order Total:** ${order.total_price}

**Shipping Address:**
{order.shipping_address.address1}
{order.shipping_address.city}, {order.shipping_address.province} {order.shipping_address.zip}

**Tracking Number:** {order.fulfillments[0].tracking_number if order.fulfillments else 'Processing'}

**Order Date:** {order.created_at.strftime('%B %d, %Y')}

---

**Available Actions:**
"""
        
        if order.financial_status == 'pending' or order.fulfillment_status == None:
            response += f"\n🚫 **Cancel Order** - Reply 'cancel order {order_number}'"
        
        if order.fulfillment_status == 'fulfilled':
            response += f"\n🔄 **Return Order** - Reply 'return order {order_number}'"
        
        return response
        
    except Exception as e:
        return f"❌ Error tracking order: {str(e)}"

def cancel_order_real(order_number):
    """Cancel REAL Shopify order"""
    if not shopify_connected:
        return "❌ Shopify integration not configured."
    
    try:
        orders = shopify.Order.find(name=f"#{order_number}")
        
        if not orders:
            return f"❌ Order #{order_number} not found."
        
        order = orders[0]
        
        if order.fulfillment_status in ['fulfilled', 'partial']:
            return f"""
❌ **Cannot Cancel Order #{order_number}**

**Reason:** Order has already been fulfilled/shipped.

**Alternative:** You can initiate a return instead.
Type: "return order {order_number}"
"""
        
        order.cancel()
        
        return f"""
✅ **Order #{order_number} Cancelled Successfully!**

**Refund Details:**
• Amount: ${order.total_price}
• Method: Original payment method
• Processing Time: 3-5 business days
• Confirmation email sent to: {order.email}

😊 **We're sorry to see this order go!**

💰 Use code **COMEBACK20** for 20% off your next order!
"""
        
    except Exception as e:
        return f"❌ Error cancelling order: {str(e)}"

def return_order_real(order_number):
    """Process REAL Shopify return"""
    if not shopify_connected:
        return "❌ Shopify integration not configured."
    
    try:
        orders = shopify.Order.find(name=f"#{order_number}")
        
        if not orders:
            return f"❌ Order #{order_number} not found."
        
        order = orders[0]
        
        if order.fulfillment_status != 'fulfilled':
            return f"""
❌ **Cannot Return Order #{order_number}**

**Reason:** Order hasn't been delivered yet.

Returns can only be initiated after delivery.
"""
        
        order.note = f"Return requested on {datetime.now().strftime('%Y-%m-%d')}"
        order.save()
        
        return f"""
✅ **Return Initiated for Order #{order_number}**

**Return Details:**
• Customer: {order.customer.first_name} {order.customer.last_name}
• Order Total: ${order.total_price}

📧 **Confirmation sent to:** {order.email}

💝 **Sorry these didn't work out!**
Use **RETURN15** for 15% off your next order.
"""
        
    except Exception as e:
        return f"❌ Error processing return: {str(e)}"

def recommend_products_real(category=None, budget=None):
    """Get REAL products from Shopify"""
    if not shopify_connected:
        return "❌ Shopify integration not configured."
    
    try:
        products = shopify.Product.find(limit=50)
        
        if category:
            products = [p for p in products if category.lower() in p.product_type.lower()]
        
        if budget:
            products = [p for p in products if float(p.variants[0].price) <= budget]
        
        products = sorted(products, key=lambda x: x.created_at, reverse=True)[:3]
        
        if not products:
            return "😕 No products found matching your criteria."
        
        response = "✨ **Perfect Recommendations For You:**\n\n"
        
        for product in products:
            variant = product.variants[0]
            stock_status = "✅ In Stock" if variant.inventory_quantity > 10 else f"⚠️ Only {variant.inventory_quantity} left!"
            
            response += f"""
---
**{product.title}**
💰 ${variant.price}
📦 {stock_status}
🔗 https://{SHOPIFY_CONFIG['shop_url']}/products/{product.handle}

"""
        
        return response
        
    except Exception as e:
        return f"❌ Error fetching products: {str(e)}"

# ============================================
# DEMO MODE FUNCTIONS (Fallback)
# ============================================

def track_order_demo(order_number):
    """Track order in demo mode"""
    order_num = order_number.strip().upper()
    
    if order_num in SAMPLE_ORDERS:
        order = SAMPLE_ORDERS[order_num]
        
        response = f"""
📦 **Order Tracking - #{order['order_number']}** (DEMO)

**Status:** {order['status']} ✅

**Items Ordered:**
{chr(10).join(['• ' + item for item in order['items']])}

**Order Total:** ${order['total']:.2f}

**Tracking Number:** {order['tracking']}

**Estimated Delivery:** {order['estimated_delivery']}

---

**Available Actions:**
"""
        
        if order['can_cancel']:
            response += f"\n🚫 **Cancel Order** - Reply 'cancel order {order_num}'"
        
        if order['can_return']:
            response += f"\n🔄 **Return Order** - Reply 'return order {order_num}'"
        
        return response
    else:
        return f"❌ Order #{order_num} not found in demo system.\n\nTry: 12345, 67890, or 54321"

def cancel_order_demo(order_number):
    """Cancel order in demo mode"""
    order_num = order_number.strip().upper()
    
    if order_num in SAMPLE_ORDERS:
        order = SAMPLE_ORDERS[order_num]
        
        if order['can_cancel']:
            return f"""
✅ **Order #{order_num} Cancelled Successfully!** (DEMO)

**Refund Details:**
• Amount: ${order['total']:.2f}
• Processing Time: 3-5 business days

💰 Use code **COMEBACK20** for 20% off your next order!
"""
        else:
            return f"❌ Cannot cancel order #{order_num} - Status: {order['status']}"
    else:
        return "❌ Order not found."

def return_order_demo(order_number):
    """Return order in demo mode"""
    order_num = order_number.strip().upper()
    
    if order_num in SAMPLE_ORDERS:
        order = SAMPLE_ORDERS[order_num]
        
        if order['can_return']:
            return f"""
✅ **Return Initiated for Order #{order_num}** (DEMO)

**Refund Amount:** ${order['total']:.2f}

📧 Check your email for return shipping label!

💝 Use **RETURN15** for 15% off your next order.
"""
        else:
            return f"❌ Cannot return order #{order_num} - Status: {order['status']}"
    else:
        return "❌ Order not found."

def recommend_products_demo(category=None, budget=None):
    """Recommend products in demo mode"""
    
    if category:
        filtered = [p for p in PRODUCTS if category.lower() in p['category'].lower() or category.lower() in p['name'].lower()]
    else:
        filtered = PRODUCTS
    
    if budget:
        filtered = [p for p in filtered if p['price'] <= budget]
    
    if not filtered:
        filtered = PRODUCTS[:3]
    
    filtered = sorted(filtered, key=lambda x: x['rating'], reverse=True)[:3]
    
    response = "✨ **Perfect Recommendations For You:** (DEMO)\n\n"
    
    for product in filtered:
        stock_status = "✅ In Stock" if product['stock'] > 10 else f"⚠️ Only {product['stock']} left!"
        
        response += f"""
---
{product['image']} **{product['name']}**
💰 ${product['price']:.2f}
⭐ {product['rating']}/5.0
📦 {stock_status}

"""
    
    return response

# ============================================
# WRAPPER FUNCTIONS (Auto-select Real or Demo)
# ============================================

def track_order(order_number):
    """Track order - auto select real or demo"""
    if shopify_connected:
        return track_order_real(order_number)
    else:
        return track_order_demo(order_number)

def cancel_order(order_number):
    """Cancel order - auto select real or demo"""
    if shopify_connected:
        return cancel_order_real(order_number)
    else:
        return cancel_order_demo(order_number)

def return_order(order_number):
    """Return order - auto select real or demo"""
    if shopify_connected:
        return return_order_real(order_number)
    else:
        return return_order_demo(order_number)

def recommend_products(category=None, budget=None):
    """Recommend products - auto select real or demo"""
    if shopify_connected:
        return recommend_products_real(category, budget)
    else:
        return recommend_products_demo(category, budget)

# ============================================
# HELPER FUNCTIONS
# ============================================

def capture_lead(name=None, email=None):
    """Capture user information"""
    if email:
        st.session_state.user_email = email
        st.session_state.user_name = name if name else "Valued Customer"
        
        return f"""
🎉 **Welcome to the VIP Club, {st.session_state.user_name}!**

**Your Welcome Gift:** 🎁
Use code **VIP20** for 20% off your first order!

Check your email ({email}) for exclusive deals!
"""
    else:
        return "💌 Join our VIP Club! Just reply with your email: 'my email is you@email.com'"

def upsell_offer():
    """Generate upsell offers"""
    return """
🎉 **Special Offer Just For You!**

**Buy 2, Get 1 50% OFF**

**Plus:** Use code **BUNDLE15** for extra 15% off!

Interested? Tell me what you're shopping for!
"""

# ============================================
# MAIN RESPONSE FUNCTION
# ============================================

def get_bot_response(user_message):
    """Generate intelligent responses"""
    
    msg = user_message.lower()
    
    # ORDER TRACKING
    if any(word in msg for word in ['track', 'tracking', 'where is my order']):
        words = user_message.split()
        for word in words:
            if word.isdigit() and len(word) == 5:
                return track_order(word)
        
        return "📦 To track your order, reply with: 'track order 12345' (use your order number)\n\n**Demo:** Try 'track order 12345'"
    
    # CANCEL ORDER
    if 'cancel order' in msg:
        words = user_message.split()
        for word in words:
            if word.isdigit():
                return cancel_order(word)
        return "Please provide order number. Example: 'cancel order 12345'"
    
    # RETURN ORDER
    if 'return order' in msg or 'refund order' in msg:
        words = user_message.split()
        for word in words:
            if word.isdigit():
                return return_order(word)
        return "Please provide order number. Example: 'return order 54321'"
    
    # PRODUCT RECOMMENDATIONS
    if any(word in msg for word in ['recommend', 'show me', 'looking for', 'need']):
        categories = ['dress', 'shoe', 'jean', 'jacket', 'bag']
        for cat in categories:
            if cat in msg:
                return recommend_products(category=cat)
        
        if '$' in msg or 'under' in msg:
            words = user_message.replace('$', '').split()
            for word in words:
                if word.isdigit():
                    return recommend_products(budget=float(word))
        
        return recommend_products()
    
    # LEAD CAPTURE
    if '@' in msg and '.' in msg:
        words = user_message.split()
        email = [word for word in words if '@' in word and '.' in word][0]
        name_words = [w for w in words if w.lower() not in ['my', 'email', 'is'] and '@' not in w]
        name = ' '.join(name_words[:2]) if name_words else None
        return capture_lead(name=name, email=email)
    
    # DEALS & OFFERS
    if any(word in msg for word in ['deal', 'discount', 'offer', 'sale', 'coupon']):
        return upsell_offer()
    
    # GREETING
    if any(word in msg for word in ['hi', 'hello', 'hey']):
        return f"""Hello! 😊 Welcome to {STORE_CONFIG['name']}!

**Try these:**
• "track order 12345" - Track an order
• "show me dresses" - Get recommendations
• "any deals?" - See current offers
• "my email is test@email.com" - Join VIP club

What can I help you with?"""
    
    # SHIPPING
    if any(word in msg for word in ['ship', 'delivery']):
        return f"""📦 **Shipping Info:**

✅ Free shipping on orders ${STORE_CONFIG['free_shipping']}+
✅ Standard: {STORE_CONFIG['delivery_days']} business days
✅ Express: 1-2 days (+$15)

Track anytime: "track order [number]"
"""
    
    # RETURNS
    if any(word in msg for word in ['return', 'refund']):
        return f"""🔄 **Returns:**

✅ {STORE_CONFIG['return_days']}-day free returns
✅ Free return shipping
✅ Full refund in 5-7 days

**Start return:** "return order [number]"
**Demo:** Try "return order 54321"
"""
    
    # PAYMENT
    if any(word in msg for word in ['payment', 'pay']):
        return """💳 **Payment Methods:**

✅ Credit/Debit Cards
✅ PayPal
✅ Apple Pay
✅ Google Pay

🔒 100% Secure checkout!
"""
    
    # CONTACT
    if any(word in msg for word in ['contact', 'email', 'phone']):
        return f"""📞 **Contact:**

📧 {STORE_CONFIG['email']}
📱 {STORE_CONFIG['phone']}
⏰ Mon-Fri, 9AM-6PM

But I'm here now! How can I help? 😊
"""
    
    # THANK YOU
    if any(word in msg for word in ['thank', 'thanks']):
        return "You're welcome! 😊\n\nAnything else I can help with?"
    
    # DEFAULT
    return f"""I can help you with:

**📦 Orders:**
• "track order 12345"
• "cancel order 67890"
• "return order 54321"

**🔍 Shopping:**
• "show me dresses"
• "products under $100"

**💰 Deals:**
• "any discounts?"

**What would you like to do?**"""

# ============================================
# STREAMLIT UI
# ============================================

# Title
st.title(f"🛍️ {STORE_CONFIG['name']} AI Assistant")
st.markdown("### Your Personal Shopping Helper 24/7")

# Sidebar
with st.sidebar:
    st.header(f"🛍️ {STORE_CONFIG['name']}")
    
    # Show connection status
    if shopify_connected:
        st.success("✅ LIVE - Real Shopify Connected")
    else:
        st.info("📋 DEMO MODE - Using sample data")
    
    st.markdown("---")
    
    st.subheader("🔥 Try These!")
    st.code("track order 12345")
    st.code("show me dresses")
    st.code("any deals?")
    st.code("my email is test@email.com")
    
    st.markdown("---")
    
    st.metric("Messages", len(st.session_state.messages))
    
    if st.button("🗑️ New Chat", use_container_width=True):
        st.session_state.messages = [{
            "role": "assistant",
            "content": f"Fresh start! How can I help you at {STORE_CONFIG['name']}?"
        }]
        st.rerun()
    
    st.markdown("---")
    
    st.subheader("📞 Support")
    st.markdown(f"""
📧 {STORE_CONFIG['email']}  
📱 {STORE_CONFIG['phone']}
""")

# Display chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if user_input := st.chat_input("Type your message..."):
    
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("user"):
        st.markdown(user_input)
    
    with st.chat_message("assistant"):
        with st.spinner("✨ Thinking..."):
            response = get_bot_response(user_input)
            st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666;'>
    <p>⚡ Powered by AI | © 2024 {STORE_CONFIG['name']}</p>
</div>
""", unsafe_allow_html=True)
