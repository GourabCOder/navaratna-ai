document.addEventListener("DOMContentLoaded", function () {

/* ==========================================================
   GEM DATA
========================================================== */

const gemsData = [
{ id:"ruby", name:"Ruby", frames:[] },
{ id:"pearl", name:"Pearl", frames:[] },
{ id:"coral", name:"Red Coral", frames:[] },
{ id:"emerald", name:"Emerald", frames:[] },
{ id:"yellow_sapphire", name:"Yellow Sapphire", frames:[] },
{ id:"diamond", name:"Diamond", frames:[] },
{ id:"blue_sapphire", name:"Blue Sapphire", frames:[] },
{ id:"hessonite", name:"Hessonite", frames:[] },
{ id:"cat_eye", name:"Cat Eye", frames:[] }
];

/* Removed canvas scroll animation completely to improve mobile performance */

/* ==========================================================
   SEARCH SYSTEM
========================================================== */

const searchInput = document.getElementById('gem-search');
const suggestionsList = document.getElementById('search-suggestions');

if(searchInput && suggestionsList) {
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase().trim();
        
        // Clear suggestions if empty
        if (!query) {
            suggestionsList.style.display = 'none';
            return;
        }

        // Filter gems
        const matches = gemsData.filter(g => g.name.toLowerCase().includes(query) || g.id.toLowerCase().includes(query));
        
        // Build suggestion HTML
        if (matches.length > 0) {
            suggestionsList.innerHTML = matches.map(m => `
                <li onclick="window.scrollToGemSection('${m.id}')">${m.name}</li>
            `).join('');
            suggestionsList.style.display = 'block';
        } else {
            suggestionsList.style.display = 'none';
        }
    });

    // Search on ENTER
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            window.searchToGem();
        }
    });

    // Hide dropdown when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.search-container') && !e.target.closest('.search-suggestions')) {
            suggestionsList.style.display = 'none';
        }
    });
}

window.searchToGem = function() {
    if(!searchInput) return;
    const query = searchInput.value.toLowerCase().trim();
    if (!query) return;

    const match = gemsData.find(g => g.name.toLowerCase().includes(query) || g.id.toLowerCase().includes(query));
    
    if (match) {
        window.scrollToGemSection(match.id);
    } else {
        window.showToast("Gem not found");
    }
};

window.scrollToGemSection = function(id) {
    const section = document.getElementById(id);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth', block: 'center' });
        
        // Remove previous highlights
        document.querySelectorAll('.gem-card.highlight').forEach(el => el.classList.remove('highlight'));
        
        // Add highlight
        section.classList.add('highlight');
        
        if(suggestionsList) suggestionsList.style.display = 'none';
        if(searchInput) searchInput.value = '';
    }
};

/* ==========================================================
   CART SYSTEM
========================================================== */

let cart = [];

window.addToCart = function(name,price,id){

const exists = cart.find(item=>item.id===id);

if(exists){
showToast(`${name} already in cart`);
return;
}

cart.push({name,price,id});
updateCartUI();

};

window.removeFromCart = function(id) {
    cart = cart.filter(item => item.id !== id);
    window.updateCartUI();
};

window.updateCartUI = function(){

const counter = document.getElementById("cart-counter");
const list = document.getElementById("cart-list");
const totalNode = document.getElementById("cart-total");

if(counter) counter.innerText = cart.length;

if(!list || !totalNode) return;

if(cart.length===0){

list.innerHTML = `<li class="cart-empty-msg">Your cart is empty</li>`;
totalNode.innerText="₹0";
return;

}

let total = 0;

list.innerHTML = cart.map(item=>{

total += item.price;

return `
<li class="cart-item">
<div class="cart-item-info">
<span class="cart-item-name">${item.name}</span>
<span class="cart-item-price">₹${item.price.toLocaleString('en-IN')}</span>
</div>
<button class="remove-item" onclick="window.removeFromCart('${item.id}')">✕</button>
</li>
`;

}).join("");

totalNode.innerText=`₹${total.toLocaleString('en-IN')}`;

};

let pendingPurchaseItems = [];
let isCartCheckout = false;

window.checkoutCart = function() {
    if (cart.length === 0) return;
    
    if (!window.userLoggedIn) {
        window.location.href = '/login';
        return;
    }
    
    window.toggleCart(); // Close cart
    
    isCartCheckout = true;
    pendingPurchaseItems = [...cart];
    
    const total = cart.reduce((sum, item) => sum + item.price, 0);
    const multiNames = cart.map(c => c.name).join(', ');
    
    const nameNode = document.getElementById('purchase-item-name');
    const priceNode = document.getElementById('purchase-item-price');
    
    if(nameNode) nameNode.innerText = multiNames.length > 30 ? multiNames.substring(0, 30) + '...' : multiNames;
    if(priceNode) priceNode.innerText = `₹${total.toLocaleString('en-IN')}`;
    
    window.openModal();
};

window.buyNow = function(name, price) {
    if (!window.userLoggedIn) {
        window.location.href = '/login';
        return;
    }

    isCartCheckout = false;
    pendingPurchaseItems = [{ name, price }];

    const nameNode = document.getElementById('purchase-item-name');
    
    if(nameNode) nameNode.innerText = name;
    
    window.openModal();
};

let currentPurchaseStep = 1;

window.openModal = function() {
    const modal = document.getElementById('purchase-modal');
    const overlay = document.getElementById('purchase-modal-overlay');
    
    if(modal && overlay) {
        currentPurchaseStep = 1;
        
        // Reset view
        if(document.getElementById('step-1-weight')) document.getElementById('step-1-weight').style.display = 'block';
        if(document.getElementById('step-2-details')) document.getElementById('step-2-details').style.display = 'none';
        if(document.getElementById('step-3-qr')) document.getElementById('step-3-qr').style.display = 'none';
        if(document.getElementById('purchase-price-display')) document.getElementById('purchase-price-display').style.display = 'none';
        
        if(document.getElementById('order-weight')) document.getElementById('order-weight').value = '';
        if(document.getElementById('order-name')) document.getElementById('order-name').value = '';
        if(document.getElementById('order-address')) document.getElementById('order-address').value = '';
        
        const nextBtn = document.getElementById('next-step-btn');
        if(nextBtn) {
            nextBtn.innerText = "Calculate Price";
            nextBtn.disabled = false;
            nextBtn.style.display = 'inline-block';
        }

        const completedBtn = document.getElementById('completed-payment-btn');
        if (completedBtn) {
            completedBtn.style.display = 'none';
        }
        
        const cancelBtn = document.getElementById('cancel-purchase-btn');
        if(cancelBtn) {
            cancelBtn.innerText = "Cancel";
            cancelBtn.style.display = 'inline-block';
        }
        
        modal.style.display = 'block';
        overlay.style.display = 'block';
        
        setTimeout(() => {
            modal.style.opacity = '1';
            overlay.style.opacity = '1';
        }, 10);
    }
};

window.closeModal = function() {
    const modal = document.getElementById('purchase-modal');
    const overlay = document.getElementById('purchase-modal-overlay');
    
    if(modal && overlay) {
        modal.style.opacity = '0';
        overlay.style.opacity = '0';
        
        setTimeout(() => {
            modal.style.display = 'none';
            overlay.style.display = 'none';
        }, 300);
    }
};

window.nextPurchaseStep = async function() {
    const nextBtn = document.getElementById('next-step-btn');
    if(!nextBtn) return;
    
    const gemstoneName = pendingPurchaseItems.length > 0 ? pendingPurchaseItems[0].name : "Unknown";
    
    if (currentPurchaseStep === 1) {
        const weightNode = document.getElementById('order-weight');
        const weight = weightNode ? parseFloat(weightNode.value) : 0;
        
        if (!weight || weight <= 0) {
            window.showToast("Weight must be greater than 0");
            return;
        }
        
        nextBtn.disabled = true;
        nextBtn.innerText = "Calculating...";
        
        try {
            const res = await fetch('/calculate-price', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ gemstone: gemstoneName, weight: weight })
            });
            const data = await res.json();
            
            if (data.status === 'success') {
                document.getElementById('purchase-item-price').innerText = data.total_price.toLocaleString('en-IN');
                document.getElementById('purchase-price-display').style.display = 'block';
                
                document.getElementById('step-1-weight').style.display = 'none';
                document.getElementById('step-2-details').style.display = 'block';
                
                currentPurchaseStep = 2;
                nextBtn.innerText = "Confirm Order";
            } else {
                window.showToast(data.message || "Error calculating price");
                nextBtn.innerText = "Calculate Price";
            }
        } catch (error) {
            console.error("Calculate price error", error);
            window.showToast("Error processing request.");
            nextBtn.innerText = "Calculate Price";
        }
        nextBtn.disabled = false;
        
    } else if (currentPurchaseStep === 2) {
        const orderName = document.getElementById('order-name') ? document.getElementById('order-name').value.trim() : "";
        const orderAddress = document.getElementById('order-address') ? document.getElementById('order-address').value.trim() : "";
        const orderWeight = document.getElementById('order-weight') ? document.getElementById('order-weight').value : "";

        if (!orderName || !orderAddress) {
            window.showToast("Name and address cannot be empty");
            return;
        }

        nextBtn.disabled = true;
        nextBtn.innerText = "Processing...";

        try {
            const res = await fetch('/place-order', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    gemstone: gemstoneName,
                    weight: orderWeight || 0,
                    name: orderName,
                    address: orderAddress
                })
            });
            const data = await res.json();
            
            if (data.status === 'success') {
                document.getElementById('step-2-details').style.display = 'none';
                document.getElementById('step-3-qr').style.display = 'block';
                
                document.getElementById('qr-success-message').innerText = data.message || "Order placed successfully. Complete payment using QR.";
                document.getElementById('payment-qr-img').src = data.qr_code;
                
                // Save to history list logic
                await fetch('/add_purchase', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        gem_name: gemstoneName,
                        price: data.price || 0
                    })
                });
                
                nextBtn.style.display = 'none';
                document.getElementById('cancel-purchase-btn').innerText = "Close";
                
                const completedBtn = document.getElementById('completed-payment-btn');
                if (completedBtn) {
                    completedBtn.style.display = 'inline-block';
                }
                
                if (isCartCheckout) {
                    cart = [];
                    window.updateCartUI();
                }
            } else {
                window.showToast(data.message || "Error processing purchase");
                nextBtn.innerText = "Confirm Order";
                nextBtn.disabled = false;
            }
        } catch (error) {
            console.error("Purchase error", error);
            window.showToast("Error processing purchase");
            nextBtn.innerText = "Confirm Order";
            nextBtn.disabled = false;
        }
    }
};

window.completePayment = function() {
    window.showToast("Order placed successfully. Thank you!");
    window.closeModal();
};

/* ==========================================================
   HISTORY MODAL
========================================================== */

window.toggleHistory = async function() {
    const historyModal = document.getElementById('history-modal');
    if(!historyModal) return;
    
    historyModal.classList.toggle('active');
    
    const cartDropdown = document.getElementById('cart-dropdown');
    if(cartDropdown) {
        cartDropdown.classList.remove('active');
        cartDropdown.style.display = 'none';
    }
    
    const aiWindow = document.getElementById('ai-chat-window');
    if(aiWindow) {
        aiWindow.classList.remove('active');
        aiWindow.style.display = 'none';
    }

    if (historyModal.classList.contains('active')) {
        // Fetch history
        try {
            const res = await fetch('/get_history');
            const data = await res.json();
            
            if (data.status === 'success') {
                const list = document.getElementById('history-list');
                const totalNode = document.getElementById('history-total');
                
                if(!list || !totalNode) return;
                
                if (data.history.length === 0) {
                    list.innerHTML = `<li style="text-align:center;color:var(--text-dim);margin-top:20px;">No purchases yet.</li>`;
                    totalNode.innerText = '₹0';
                    return;
                }
                
                let total = 0;
                list.innerHTML = data.history.map(item => {
                    total += item.price;
                    const dateObj = new Date(item.date);
                    const formattedDate = dateObj.toLocaleDateString() + ' ' + dateObj.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
                    
                    return `
                        <li class="history-item">
                            <div class="history-item-details">
                                <span class="history-item-name">${item.gem_name}</span>
                                <span class="history-item-date">${formattedDate}</span>
                            </div>
                            <span class="history-item-price">₹${item.price.toLocaleString('en-IN')}</span>
                        </li>
                    `;
                }).join('');
                
                totalNode.innerText = `₹${total.toLocaleString('en-IN')}`;
            }
        } catch (error) {
            console.error(error);
        }
    }
};

/* ==========================================================
   HEADER BUTTONS
========================================================== */

window.toggleCart = function(){

const cartDropdown = document.getElementById("cart-dropdown");

if(!cartDropdown) return;

if(cartDropdown.classList.contains("active")){
cartDropdown.classList.remove("active");
cartDropdown.style.display="none";
}else{
cartDropdown.classList.add("active");
cartDropdown.style.display="block";
}

const historyModal = document.getElementById("history-modal");
if (historyModal) {
    historyModal.classList.remove("active");
}

};

window.toggleAIChat = function(){

if (!window.userLoggedIn) {
    window.showToast("Please login to access Navaratna AI chatbot.");
    setTimeout(() => {
        window.location.href = '/login';
    }, 1500);
    return;
}

const aiWindow = document.getElementById("ai-chat-window");

if(!aiWindow) return;

if(aiWindow.classList.contains("active")){
aiWindow.classList.remove("active");
aiWindow.style.display="none";
}else{
aiWindow.classList.add("active");
aiWindow.style.display="flex";
}

const historyModal = document.getElementById("history-modal");
if (historyModal) {
    historyModal.classList.remove("active");
}

};

/* ==========================================================
   AI CHAT SYSTEM
========================================================== */

window.handleChatEnter = function(e){
    if(e.key==="Enter"){
        sendChatMessage();
    }
};

window.sendChatMessage = async function(){
    const input = document.getElementById("chat-input-field");
    const msgArea = document.getElementById("chat-messages");

    if(!input || !msgArea) return;

    const msg = input.value.trim();
    if(!msg) return;

    msgArea.innerHTML += `<div class="message user-message">${msg}</div>`;
    input.value="";
    msgArea.scrollTop = msgArea.scrollHeight;

    const typingId = "typing-" + Date.now();
    const typingTimer = setTimeout(() => {
        msgArea.innerHTML += `<div class="message ai-message" id="${typingId}">
        Typing...
        </div>`;
        msgArea.scrollTop = msgArea.scrollHeight;
    }, 1000);

    try {
        const response = await fetch("/ai_prediction", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_message: msg })
        });

        const data = await response.json();
        
        clearTimeout(typingTimer);
        const typingIndicator = document.getElementById(typingId);
        if (typingIndicator) typingIndicator.remove();

        const replyHtml = data.reply ? data.reply.replace(/\n/g, '<br>') : "No reply.";
        msgArea.innerHTML += `<div class="message ai-message">${replyHtml}</div>`;
        msgArea.scrollTop = msgArea.scrollHeight;

        if (data.recommended_gemstone && data.recommended_gemstone !== "Unknown" && data.recommended_gemstone !== "Error") {
            const loweredRec = data.recommended_gemstone.toLowerCase();
            const match = gemsData.find(g => g.name.toLowerCase() === loweredRec || loweredRec.includes(g.id.toLowerCase()));
            if (match) {
                const section = document.getElementById(match.id);
                if(section) {
                    window.scrollToGemSection(match.id);
                    const badge = document.getElementById("badge-" + match.id);
                    if(badge) badge.style.display = "block";
                }
            }
        }
    } catch(error) {
        clearTimeout(typingTimer);
        const typingIndicator = document.getElementById(typingId);
        if (typingIndicator) typingIndicator.remove();
        
        msgArea.innerHTML += `<div class="message ai-message">Something went wrong, but I’m still here to help you.</div>`;
        console.error(error);
    }
};

// Reset option if needed
window.resetChatSession = async function() {
    const msgArea = document.getElementById("chat-messages");
    if(msgArea) {
        msgArea.innerHTML = `<div class="message ai-message">
        Hello! I am your gemstone consultant. How can I assist you today?
        </div>`;
    }
    try {
        await fetch("/ai_prediction", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ reset: true })
        });
    } catch(error) {
        console.error("Reset failed", error);
    }
};

/* ==========================================================
   TOAST
========================================================== */

let toastTimeout;

window.showToast = function(message){

const toast = document.getElementById("toast-notification");

if(!toast) return;

toast.innerText = message;
toast.classList.add("show");

clearTimeout(toastTimeout);

toastTimeout = setTimeout(()=>{
toast.classList.remove("show");
},3000);

}

window.openCart = function() {
    console.log("Cart opened");
    window.toggleCart();
};

});
