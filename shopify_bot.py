import streamlit as st
from datetime import datetime, timedelta
import os

# ============================================
# SHOPIFY INTEGRATION
# ============================================

# Set to True when connecting to real Shopify store
USE_REAL_SHOPIFY = False  # ← Change to True for real integration

SHOPIFY_AVAILABLE = False

if USE_REAL_SHOPIFY:
    try:
        import shopify
        SHOPIFY_AVAILABLE = True
    except ImportError:
        SHOPIFY_AVAILABLE = False

# ============================================
# SHOPIFY CONFIGURATION
# ============================================
# Option 1: Hardcode (for testing only)
# Option 2: Use .env file (recommended for production)
#   Create .env file with:
#   SHOPIFY_SHOP_URL=your-store.myshopify.com
#   SHOPIFY_API_KEY=your_api_key
#   SHOPIFY_API_PASSWORD=shpat_your_access_token

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, use hardcoded values

SHOPIFY_CONFIG = {
    "shop_url": os.getenv("SHOPIFY_SHOP_URL", "your-store.myshopify.com"),
    "api_key": os.getenv("SHOPIFY_API_KEY", "your_api_key_here"),
    "api_password": os.getenv("SHOPIFY_API_PASSWORD", "shpat_your_access_token_here"),
}

# ============================================
# FIX 1: Corrected connect_to_shopify function
# Bug: Old code put credentials in URL (broken in modern Shopify)
# Fix: Use X-Shopify-Access-Token header instead
# ============================================

def connect_to_shopify(shop_url, api_key, api_password):
    """Connect to client's Shopify store"""
    if not SHOPIFY_AVAILABLE:
        return False

    try:
        api_version = "2024-01"
        shopify.ShopifyResource.set_site(
            f"https://{shop_url}/admin/api/{api_version}"
        )
        shopify.ShopifyResource.set_headers({
            "X-Shopify-Access-Token": api_password  # ✅ Correct auth method
        })

        # Test the connection by fetching shop info
        shop = shopify.Shop.current()
        st.sidebar.success(f"✅ Connected to: {shop.name}")
        return True

    except Exception as e:
        st.sidebar.error(f"❌ Shopify connection failed: {e}")
        return False


# Connect to Shopify if enabled
shopify_connected = False
if USE_REAL_SHOPIFY and SHOPIFY_AVAILABLE:
    shopify_connected = connect_to_shopify(
        SHOPIFY_CONFIG["shop_url"],
        SHOPIFY_CONFIG["api_key"],
        SHOPIFY_CONFIG["api_password"],
    )
elif USE_REAL_SHOPIFY and not SHOPIFY_AVAILABLE:
    st.warning("⚠️ Shopify library not installed. Run: pip install shopify-python-api")

# ============================================
# Page Configuration
# ============================================

st.set_page_config(
    page_title="AI Shopping Assistant",
    page_icon="🛍️",
    layout="centered",
)

st.markdown("""
<style>
    .main { background-color: #f5f5f5; }
    .stTextInput>div>div>input { background-color: white; }
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
    "currency": "$",
}

# ============================================
# SAMPLE PRODUCTS DATABASE (Demo Mode)
# ============================================

PRODUCTS = [
    {"id": 1, "name": "Classic Denim Jacket",   "price": 89.99,  "category": "Outerwear",    "rating": 4.5, "stock": 15, "image": "🧥"},
    {"id": 2, "name": "White Sneakers",          "price": 79.99,  "category": "Shoes",        "rating": 4.8, "stock": 8,  "image": "👟"},
    {"id": 3, "name": "Summer Floral Dress",     "price": 69.99,  "category": "Dresses",      "rating": 4.7, "stock": 20, "image": "👗"},
    {"id": 4, "name": "Leather Crossbody Bag",   "price": 129.99, "category": "Accessories",  "rating": 4.9, "stock": 12, "image": "👜"},
    {"id": 5, "name": "Slim Fit Black Jeans",    "price": 59.99,  "category": "Bottoms",      "rating": 4.6, "stock": 25, "image": "👖"},
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
        "can_return": False,
    },
    "67890": {
        "order_number": "67890",
        "status": "Processing",
        "items": ["Summer Floral Dress"],
        "total": 69.99,
        "tracking": "Processing",
        "estimated_delivery": (datetime.now() + timedelta(days=5)).strftime("%B %d, %Y"),
        "can_cancel": True,
        "can_return": False,
    },
    "54321": {
        "order_number": "54321",
        "status": "Delivered",
        "items": ["Leather Crossbody Bag"],
        "total": 129.99,
        "tracking": "DELIVERED",
        "estimated_delivery": "Delivered on " + (datetime.now() - timedelta(days=3)).strftime("%B %d, %Y"),
        "can_cancel": False,
        "can_return": True,
    },
}

# ============================================
# SESSION STATE INITIALIZATION
# ============================================

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                f"Hello! 👋 Welcome to **{STORE_CONFIG['name']}**! I'm your AI shopping assistant.\n\n"
                "**I can help you with:**\n\n"
                "🔍 Product recommendations\n"
                "📦 Order tracking\n"
                "🔄 Returns & exchanges\n"
                "💳 Payment & shipping info\n"
                "📧 Exclusive deals\n\n"
                "What would you like to know?"
            ),
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
    try:
        # FIX 2: Shopify API uses '#' prefix for order names
        orders = shopify.Order.find(name=f"#{order_number}", status="any")

        if not orders:
            return f"❌ Order #{order_number} not found. Please check your order number."

        order = orders[0]

        # FIX 3: Safe access to customer (guest orders may have no customer object)
        customer_name = "Guest"
        customer_email = getattr(order, "email", "N/A")
        if hasattr(order, "customer") and order.customer:
            customer_name = f"{order.customer.first_name} {order.customer.last_name}".strip()

        # FIX 4: Safe access to shipping address (digital products may not have one)
        shipping_info = "No shipping address on file."
        if hasattr(order, "shipping_address") and order.shipping_address:
            addr = order.shipping_address
            shipping_info = (
                f"{getattr(addr, 'address1', '')}\n"
                f"{getattr(addr, 'city', '')}, "
                f"{getattr(addr, 'province', '')} "
                f"{getattr(addr, 'zip', '')}"
            ).strip()

        # FIX 5: Safe access to fulfillments (order may not be fulfilled yet)
        tracking_number = "Processing — not yet shipped"
        if order.fulfillments:
            tracking_number = getattr(order.fulfillments[0], "tracking_number", "N/A") or "N/A"

        # FIX 6: Safe access to financial_status and fulfillment_status
        financial_status = getattr(order, "financial_status", "unknown").upper()
        fulfillment_status = getattr(order, "fulfillment_status", None)

        items_text = "\n".join(
            [f"• {item.name} (Qty: {item.quantity}) — ${item.price}" for item in order.line_items]
        )

        response = (
            f"📦 **Order Tracking — #{order.order_number}**\n\n"
            f"**Customer:** {customer_name}\n"
            f"**Email:** {customer_email}\n\n"
            f"**Payment Status:** {financial_status}\n"
            f"**Fulfillment Status:** {str(fulfillment_status).title() if fulfillment_status else 'Unfulfilled'}\n\n"
            f"**Items Ordered:**\n{items_text}\n\n"
            f"**Order Total:** ${order.total_price}\n\n"
            f"**Shipping Address:**\n{shipping_info}\n\n"
            f"**Tracking Number:** {tracking_number}\n\n"
            f"**Order Date:** {order.created_at[:10]}\n\n"
            "---\n**Available Actions:**"
        )

        if fulfillment_status is None:
            response += f"\n🚫 **Cancel Order** — Reply: `cancel order {order_number}`"

        if fulfillment_status == "fulfilled":
            response += f"\n🔄 **Return Order** — Reply: `return order {order_number}`"

        return response

    except Exception as e:
        return f"❌ Error tracking order: {str(e)}"


def cancel_order_real(order_number):
    """Cancel REAL Shopify order"""
    try:
        orders = shopify.Order.find(name=f"#{order_number}", status="any")

        if not orders:
            return f"❌ Order #{order_number} not found."

        order = orders[0]
        fulfillment_status = getattr(order, "fulfillment_status", None)

        if fulfillment_status in ["fulfilled", "partial"]:
            return (
                f"❌ **Cannot Cancel Order #{order_number}**\n\n"
                f"**Reason:** Order has already been fulfilled/shipped.\n\n"
                f"**Alternative:** You can initiate a return instead.\n"
                f"Type: `return order {order_number}`"
            )

        # FIX 7: cancel() needs to be called correctly — pass reason as param
        order.cancel({"reason": "customer"})

        customer_email = getattr(order, "email", "your email")

        return (
            f"✅ **Order #{order_number} Cancelled Successfully!**\n\n"
            f"**Refund Details:**\n"
            f"• Amount: ${order.total_price}\n"
            f"• Method: Original payment method\n"
            f"• Processing Time: 3–5 business days\n"
            f"• Confirmation email sent to: {customer_email}\n\n"
            "😊 **We're sorry to see this order go!**\n\n"
            "💰 Use code **COMEBACK20** for 20% off your next order!"
        )

    except Exception as e:
        return f"❌ Error cancelling order: {str(e)}"


def return_order_real(order_number):
    """Process REAL Shopify return"""
    try:
        orders = shopify.Order.find(name=f"#{order_number}", status="any")

        if not orders:
            return f"❌ Order #{order_number} not found."

        order = orders[0]
        fulfillment_status = getattr(order, "fulfillment_status", None)

        if fulfillment_status != "fulfilled":
            return (
                f"❌ **Cannot Return Order #{order_number}**\n\n"
                "**Reason:** Order hasn't been fully delivered yet.\n\n"
                "Returns can only be initiated after delivery."
            )

        # FIX 8: Correct way to add a note — fetch, update, save
        existing_note = getattr(order, "note", "") or ""
        order.note = f"{existing_note} | Return requested on {datetime.now().strftime('%Y-%m-%d')}".strip(" |")
        order.save()

        customer_name = "Valued Customer"
        customer_email = getattr(order, "email", "N/A")
        if hasattr(order, "customer") and order.customer:
            customer_name = f"{order.customer.first_name} {order.customer.last_name}".strip()

        return (
            f"✅ **Return Initiated for Order #{order_number}**\n\n"
            f"**Return Details:**\n"
            f"• Customer: {customer_name}\n"
            f"• Order Total: ${order.total_price}\n\n"
            f"📧 **Confirmation sent to:** {customer_email}\n\n"
            "💝 **Sorry these didn't work out!**\n"
            "Use **RETURN15** for 15% off your next order."
        )

    except Exception as e:
        return f"❌ Error processing return: {str(e)}"


def recommend_products_real(category=None, budget=None):
    """Get REAL products from Shopify"""
    try:
        # FIX 9: Fetch more products and handle empty results gracefully
        products = shopify.Product.find(limit=50, status="active")

        if not products:
            return "😕 No products found in the store right now."

        # Filter by category if given
        if category:
            filtered = [
                p for p in products
                if category.lower() in (p.product_type or "").lower()
                or category.lower() in (p.title or "").lower()
                or any(category.lower() in (tag or "").lower() for tag in (p.tags or "").split(","))
            ]
            products = filtered if filtered else products  # fallback to all if no match

        # Filter by budget
        if budget:
            products = [
                p for p in products
                if p.variants and float(p.variants[0].price) <= budget
            ]

        # FIX 10: Sort by created_at safely (it's a string, not datetime)
        products = sorted(products, key=lambda x: x.created_at or "", reverse=True)[:3]

        if not products:
            return "😕 No products found matching your criteria. Try a different budget or category."

        response = "✨ **Perfect Recommendations For You:**\n\n"

        for product in products:
            # FIX 11: Guard against products with no variants
            if not product.variants:
                continue

            variant = product.variants[0]
            price = float(variant.price)
            inventory = getattr(variant, "inventory_quantity", None)

            if inventory is None:
                stock_status = "✅ Available"
            elif inventory > 10:
                stock_status = "✅ In Stock"
            elif inventory > 0:
                stock_status = f"⚠️ Only {inventory} left!"
            else:
                stock_status = "❌ Out of Stock"

            product_url = f"https://{SHOPIFY_CONFIG['shop_url']}/products/{product.handle}"

            response += (
                f"---\n"
                f"**{product.title}**\n"
                f"💰 ${price:.2f}\n"
                f"📦 {stock_status}\n"
                f"🔗 [View Product]({product_url})\n\n"
            )

        return response

    except Exception as e:
        return f"❌ Error fetching products: {str(e)}"


# ============================================
# DEMO MODE FUNCTIONS (Fallback)
# ============================================

def track_order_demo(order_number):
    order_num = order_number.strip().upper()

    if order_num in SAMPLE_ORDERS:
        order = SAMPLE_ORDERS[order_num]

        items_text = "\n".join([f"• {item}" for item in order["items"]])

        response = (
            f"📦 **Order Tracking — #{order['order_number']}** *(DEMO)*\n\n"
            f"**Status:** {order['status']} ✅\n\n"
            f"**Items Ordered:**\n{items_text}\n\n"
            f"**Order Total:** ${order['total']:.2f}\n\n"
            f"**Tracking Number:** {order['tracking']}\n\n"
            f"**Estimated Delivery:** {order['estimated_delivery']}\n\n"
            "---\n**Available Actions:**"
        )

        if order["can_cancel"]:
            response += f"\n🚫 **Cancel Order** — Reply: `cancel order {order_num}`"

        if order["can_return"]:
            response += f"\n🔄 **Return Order** — Reply: `return order {order_num}`"

        return response
    else:
        return (
            f"❌ Order #{order_num} not found in demo system.\n\n"
            "**Try these demo order numbers:** `12345`, `67890`, or `54321`"
        )


def cancel_order_demo(order_number):
    order_num = order_number.strip().upper()

    if order_num in SAMPLE_ORDERS:
        order = SAMPLE_ORDERS[order_num]

        if order["can_cancel"]:
            return (
                f"✅ **Order #{order_num} Cancelled Successfully!** *(DEMO)*\n\n"
                f"**Refund Details:**\n"
                f"• Amount: ${order['total']:.2f}\n"
                f"• Processing Time: 3–5 business days\n\n"
                "💰 Use code **COMEBACK20** for 20% off your next order!"
            )
        else:
            return (
                f"❌ **Cannot Cancel Order #{order_num}**\n\n"
                f"**Reason:** Order status is *{order['status']}* — cancellation not allowed.\n\n"
                "Contact support if you need help."
            )
    else:
        return "❌ Order not found. Try demo order `67890` which can be cancelled."


def return_order_demo(order_number):
    order_num = order_number.strip().upper()

    if order_num in SAMPLE_ORDERS:
        order = SAMPLE_ORDERS[order_num]

        if order["can_return"]:
            return (
                f"✅ **Return Initiated for Order #{order_num}** *(DEMO)*\n\n"
                f"**Refund Amount:** ${order['total']:.2f}\n\n"
                "📧 Check your email for the return shipping label!\n\n"
                "💝 Use **RETURN15** for 15% off your next order."
            )
        else:
            return (
                f"❌ **Cannot Return Order #{order_num}**\n\n"
                f"**Reason:** Order status is *{order['status']}*.\n\n"
                "Only delivered orders can be returned. Try demo order `54321`."
            )
    else:
        return "❌ Order not found. Try demo order `54321` which can be returned."


def recommend_products_demo(category=None, budget=None):
    filtered = PRODUCTS

    if category:
        filtered = [
            p for p in filtered
            if category.lower() in p["category"].lower()
            or category.lower() in p["name"].lower()
        ]

    if budget:
        filtered = [p for p in filtered if p["price"] <= budget]

    # Fallback to all products if nothing matches
    if not filtered:
        filtered = PRODUCTS

    filtered = sorted(filtered, key=lambda x: x["rating"], reverse=True)[:3]

    response = "✨ **Perfect Recommendations For You:** *(DEMO)*\n\n"

    for product in filtered:
        stock_status = (
            "✅ In Stock" if product["stock"] > 10 else f"⚠️ Only {product['stock']} left!"
        )

        response += (
            f"---\n"
            f"{product['image']} **{product['name']}**\n"
            f"💰 ${product['price']:.2f}\n"
            f"⭐ {product['rating']}/5.0\n"
            f"📦 {stock_status}\n\n"
        )

    return response


# ============================================
# WRAPPER FUNCTIONS (Auto-select Real or Demo)
# ============================================

def track_order(order_number):
    return track_order_real(order_number) if shopify_connected else track_order_demo(order_number)

def cancel_order(order_number):
    return cancel_order_real(order_number) if shopify_connected else cancel_order_demo(order_number)

def return_order(order_number):
    return return_order_real(order_number) if shopify_connected else return_order_demo(order_number)

def recommend_products(category=None, budget=None):
    return (
        recommend_products_real(category, budget)
        if shopify_connected
        else recommend_products_demo(category, budget)
    )

# ============================================
# HELPER FUNCTIONS
# ============================================

def capture_lead(name=None, email=None):
    if email:
        st.session_state.user_email = email
        st.session_state.user_name = name if name else "Valued Customer"

        return (
            f"🎉 **Welcome to the VIP Club, {st.session_state.user_name}!**\n\n"
            "**Your Welcome Gift:** 🎁\n"
            "Use code **VIP20** for 20% off your first order!\n\n"
            f"Check your email ({email}) for exclusive deals!"
        )
    else:
        return "💌 Join our VIP Club! Reply with your email:\n`my email is you@email.com`"


def upsell_offer():
    return (
        "🎉 **Special Offer Just For You!**\n\n"
        "**Buy 2, Get 1 at 50% OFF**\n\n"
        "**Plus:** Use code **BUNDLE15** for extra 15% off!\n\n"
        "Interested? Tell me what you're shopping for!"
    )

# ============================================
# FIX 12: Improved order number extraction
# Bug: Original only checked 5-digit numbers — Shopify order numbers can be 4+ digits
# ============================================

def extract_order_number(text):
    """Extract order number from user message (handles #1001, order 1001, etc.)"""
    import re
    # Match optional # followed by digits (4 or more)
    match = re.search(r"#?(\d{4,})", text)
    return match.group(1) if match else None


def extract_email(text):
    """Extract email from user message"""
    import re
    match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    return match.group(0) if match else None


def extract_budget(text):
    """Extract budget amount from user message"""
    import re
    match = re.search(r"\$?\s*(\d+)", text)
    return float(match.group(1)) if match else None

# ============================================
# MAIN RESPONSE FUNCTION (with all fixes applied)
# ============================================

def get_bot_response(user_message):
    """Generate intelligent responses"""

    msg = user_message.lower()

    # ---- ORDER TRACKING ----
    if any(word in msg for word in ["track", "tracking", "where is my order", "where's my order"]):
        order_num = extract_order_number(user_message)
        if order_num:
            return track_order(order_num)
        return (
            "📦 To track your order, please include your order number.\n\n"
            "**Example:** `track order 12345`\n\n"
            "*(Demo: Try order numbers 12345, 67890, or 54321)*"
        )

    # ---- CANCEL ORDER ----
    if "cancel order" in msg or ("cancel" in msg and "order" in msg):
        order_num = extract_order_number(user_message)
        if order_num:
            return cancel_order(order_num)
        return "Please provide your order number.\n**Example:** `cancel order 67890`"

    # ---- RETURN / REFUND ----
    if ("return order" in msg or "refund order" in msg
            or ("return" in msg and "order" in msg)
            or ("refund" in msg and "order" in msg)):
        order_num = extract_order_number(user_message)
        if order_num:
            return return_order(order_num)
        return "Please provide your order number.\n**Example:** `return order 54321`"

    # ---- PRODUCT RECOMMENDATIONS ----
    if any(word in msg for word in ["recommend", "show me", "looking for", "need", "find", "suggest"]):
        categories = ["dress", "shoe", "jean", "jacket", "bag", "top", "shirt", "pant"]
        matched_cat = next((cat for cat in categories if cat in msg), None)

        budget = None
        if "$" in msg or "under" in msg or "below" in msg or "budget" in msg:
            budget = extract_budget(user_message)

        return recommend_products(category=matched_cat, budget=budget)

    # ---- PRODUCTS UNDER BUDGET (without recommendation keyword) ----
    if "under" in msg or "below" in msg:
        budget = extract_budget(user_message)
        if budget:
            return recommend_products(budget=budget)

    # ---- LEAD CAPTURE ----
    email = extract_email(user_message)
    if email:
        words = user_message.split()
        name_words = [
            w for w in words
            if w.lower() not in ["my", "email", "is", "it's", "its", "the", "name"] and "@" not in w
        ]
        name = " ".join(name_words[:2]).strip() if name_words else None
        return capture_lead(name=name if name else None, email=email)

    # ---- DEALS & OFFERS ----
    if any(word in msg for word in ["deal", "discount", "offer", "sale", "coupon", "promo", "code"]):
        return upsell_offer()

    # ---- GREETING ----
    if any(word in msg for word in ["hi", "hello", "hey", "hola", "howdy", "sup"]):
        return (
            f"Hello! 😊 Welcome to **{STORE_CONFIG['name']}**!\n\n"
            "**Here's what I can do:**\n"
            "• `track order 12345` — Track an order\n"
            "• `show me dresses` — Browse products\n"
            "• `products under $80` — Filter by budget\n"
            "• `any deals?` — See current offers\n"
            "• `my email is you@email.com` — Join VIP Club\n\n"
            "What can I help you with today?"
        )

    # ---- SHIPPING ----
    if any(word in msg for word in ["ship", "delivery", "shipping", "deliver", "arrive"]):
        return (
            "📦 **Shipping Info:**\n\n"
            f"✅ **Free shipping** on orders over ${STORE_CONFIG['free_shipping']}\n"
            f"✅ **Standard:** {STORE_CONFIG['delivery_days']} business days\n"
            "✅ **Express:** 1–2 days (+$15)\n\n"
            "Track your order anytime: `track order [number]`"
        )

    # ---- RETURNS ----
    if any(word in msg for word in ["return", "refund", "exchange"]):
        return (
            "🔄 **Returns & Refunds:**\n\n"
            f"✅ **{STORE_CONFIG['return_days']}-day** free returns\n"
            "✅ Free return shipping label emailed to you\n"
            "✅ Full refund in 5–7 business days\n\n"
            "**Start a return:** `return order [number]`\n"
            "*(Demo: Try `return order 54321`)*"
        )

    # ---- PAYMENT ----
    if any(word in msg for word in ["payment", "pay", "checkout", "credit", "paypal"]):
        return (
            "💳 **Payment Methods Accepted:**\n\n"
            "✅ Visa / Mastercard / Amex\n"
            "✅ PayPal\n"
            "✅ Apple Pay\n"
            "✅ Google Pay\n"
            "✅ Shop Pay (Buy Now, Pay Later)\n\n"
            "🔒 100% Secure & Encrypted Checkout!"
        )

    # ---- CONTACT ----
    if any(word in msg for word in ["contact", "support", "help", "human", "agent", "phone"]):
        return (
            "📞 **Contact & Support:**\n\n"
            f"📧 **Email:** {STORE_CONFIG['email']}\n"
            f"📱 **Phone:** {STORE_CONFIG['phone']}\n"
            "⏰ **Hours:** Mon–Fri, 9AM–6PM EST\n\n"
            "But I'm here 24/7! How can I help? 😊"
        )

    # ---- SIZE GUIDE ----
    if any(word in msg for word in ["size", "sizing", "fit", "measurement"]):
        return (
            "📏 **Size Guide:**\n\n"
            "| Size | US | Chest | Waist |\n"
            "|------|----|-------|-------|\n"
            "| S    | 4-6 | 34\" | 27\" |\n"
            "| M    | 8-10 | 36\" | 29\" |\n"
            "| L    | 12-14 | 38\" | 31\" |\n"
            "| XL   | 16-18 | 41\" | 34\" |\n\n"
            "💡 Unsure? We recommend sizing up for a relaxed fit."
        )

    # ---- THANK YOU ----
    if any(word in msg for word in ["thank", "thanks", "thx", "ty"]):
        return "You're welcome! 😊\n\nAnything else I can help you with?"

    # ---- DEFAULT ----
    return (
        "I'm not sure I understood that 🤔 Here's what I can help with:\n\n"
        "**📦 Orders:**\n"
        "• `track order 12345`\n"
        "• `cancel order 67890`\n"
        "• `return order 54321`\n\n"
        "**🔍 Shopping:**\n"
        "• `show me dresses`\n"
        "• `products under $100`\n\n"
        "**💰 Deals & Info:**\n"
        "• `any discounts?`\n"
        "• `shipping info`\n"
        "• `return policy`\n\n"
        "What would you like to do?"
    )

# ============================================
# STREAMLIT UI
# ============================================

st.title(f"🛍️ {STORE_CONFIG['name']} AI Assistant")
st.markdown("### Your Personal Shopping Helper — 24/7")

# ---- Sidebar ----
with st.sidebar:
    st.header(f"🛍️ {STORE_CONFIG['name']}")

    if shopify_connected:
        st.success("✅ LIVE — Real Shopify Connected")
    elif USE_REAL_SHOPIFY:
        st.error("❌ Shopify connection failed — check credentials")
    else:
        st.info("📋 DEMO MODE — Using sample data")

    st.markdown("---")

    st.subheader("🔥 Try These!")
    st.code("track order 12345")
    st.code("show me dresses")
    st.code("products under $80")
    st.code("any deals?")
    st.code("my email is test@email.com")
    st.code("sizing guide")
    st.code("return order 54321")

    st.markdown("---")
    st.metric("Messages", len(st.session_state.messages))

    if st.button("🗑️ New Chat", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": f"Fresh start! 👋 How can I help you at **{STORE_CONFIG['name']}** today?",
            }
        ]
        st.session_state.user_email = None
        st.session_state.user_name = None
        st.rerun()

    st.markdown("---")
    st.subheader("📞 Support")
    st.markdown(f"📧 {STORE_CONFIG['email']}\n\n📱 {STORE_CONFIG['phone']}")

    # Show VIP status if captured
    if st.session_state.user_email:
        st.markdown("---")
        st.success(f"👑 VIP: {st.session_state.user_name}\n{st.session_state.user_email}")

# ---- Chat Display ----
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---- Chat Input ----
if user_input := st.chat_input("Type your message..."):

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("✨ Thinking..."):
            response = get_bot_response(user_input)
            st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})

# ---- Footer ----
st.markdown("---")
st.markdown(
    f"<div style='text-align:center; color:#888;'>"
    f"⚡ Powered by AI | © 2024 {STORE_CONFIG['name']}"
    f"</div>",
    unsafe_allow_html=True,
)
