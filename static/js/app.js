/**
 * L'ÉTOILE DORÉE - RESTAURANT INTERACTIVE ENGINE
 */

document.addEventListener('DOMContentLoaded', () => {
  // --- Global State ---
  let cart = JSON.parse(localStorage.getItem('luxury_restaurant_cart') || '[]');
  let allMenuItems = [];
  let currentCategory = 'all';
  let currentDiet = 'all';
  let searchQuery = '';

  // --- Helper: Get CSRF Token from Cookie ---
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
  const csrftoken = getCookie('csrftoken');

  // --- Navbar Scroll Effect ---
  const navbar = document.querySelector('.luxury-navbar');
  window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
      navbar?.classList.add('scrolled');
    } else {
      navbar?.classList.remove('scrolled');
    }
  });

  // --- Fetch Initial Menu Data for Client-Side Filtering ---
  async function loadMenuData() {
    try {
      const response = await fetch('/api/menu/');
      const data = await response.json();
      allMenuItems = data.items;
      renderMenu();
    } catch (err) {
      console.error('Error fetching menu items:', err);
    }
  }

  // --- Render Filtered Menu ---
  function renderMenu() {
    const grid = document.getElementById('menu-dish-grid');
    if (!grid) return;

    let filtered = allMenuItems.filter(item => {
      const matchesCategory = currentCategory === 'all' || item.category_slug === currentCategory;
      let matchesDiet = true;
      if (currentDiet === 'vegetarian') matchesDiet = item.is_vegetarian;
      if (currentDiet === 'vegan') matchesDiet = item.is_vegan;
      if (currentDiet === 'gluten_free') matchesDiet = item.is_gluten_free;
      if (currentDiet === 'chef_special') matchesDiet = item.is_chef_special;

      const matchesSearch = !searchQuery || 
        item.name.toLowerCase().includes(searchQuery) || 
        item.description.toLowerCase().includes(searchQuery);

      return matchesCategory && matchesDiet && matchesSearch;
    });

    if (filtered.length === 0) {
      grid.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 4rem 1rem; color: var(--text-muted);">
          <p style="font-size: 1.2rem; font-family: var(--font-serif); margin-bottom: 0.5rem;">No culinary creations match your selection.</p>
          <p style="font-size: 0.9rem;">Try adjusting your dietary filter or search terms.</p>
        </div>
      `;
      return;
    }

    grid.innerHTML = filtered.map(item => `
      <div class="dish-card" data-id="${item.id}">
        <div class="dish-img-wrap">
          <img src="${item.image_url || 'https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=800&q=80'}" alt="${item.name}" class="dish-img" loading="lazy">
          ${item.is_chef_special ? '<span class="dish-badge-special">Chef\'s Selection</span>' : ''}
          <div class="dish-badge-diet">
            ${item.is_vegetarian ? '<span class="diet-pill veg">VEG</span>' : ''}
            ${item.is_gluten_free ? '<span class="diet-pill gf">GF</span>' : ''}
          </div>
        </div>
        <div class="dish-body">
          <div class="dish-header">
            <h3 class="dish-name font-serif">${item.name}</h3>
            <span class="dish-price">$${item.price.toFixed(2)}</span>
          </div>
          <p class="dish-desc">${item.description}</p>
          <div class="dish-meta">
            <span class="dish-rating" onclick="window.openDishReviews(${item.id})" style="cursor: pointer;" title="View & Add Tasting Notes">★ ${item.rating.toFixed(1)} <span style="font-size: 0.75rem; text-decoration: underline; margin-left: 3px;">Reviews</span></span>
            <span>${item.calories ? item.calories + ' kcal • ' : ''}${item.prep_time} mins</span>
          </div>
          <div class="dish-card-actions">
            <button class="btn-add-cart" onclick="window.addToCart(${item.id})">
              <span>+ Add to Tasting Order</span>
            </button>
          </div>
        </div>
      </div>
    `).join('');
  }

  // --- Category Tabs Handling ---
  const categoryTabs = document.querySelectorAll('.category-tabs .tab-btn');
  categoryTabs.forEach(btn => {
    btn.addEventListener('click', () => {
      categoryTabs.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentCategory = btn.dataset.slug;
      renderMenu();
    });
  });

  // --- Dietary Filters Handling ---
  const dietButtons = document.querySelectorAll('.dietary-filters .dietary-btn');
  dietButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      if (btn.classList.contains('active')) {
        btn.classList.remove('active');
        currentDiet = 'all';
      } else {
        dietButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentDiet = btn.dataset.diet;
      }
      renderMenu();
    });
  });

  // --- Search Input Handling ---
  const searchInput = document.getElementById('menu-search-input');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      searchQuery = e.target.value.toLowerCase().trim();
      renderMenu();
    });
  }

  // --- Cart Drawer Management ---
  const cartDrawer = document.getElementById('cart-drawer');
  const cartOverlay = document.getElementById('cart-overlay');
  const cartToggleBtn = document.getElementById('cart-toggle-btn');
  const cartCloseBtn = document.getElementById('cart-close-btn');

  function openCart() {
    cartDrawer?.classList.add('open');
    cartOverlay?.classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  function closeCart() {
    cartDrawer?.classList.remove('open');
    cartOverlay?.classList.remove('open');
    document.body.style.overflow = '';
  }

  cartToggleBtn?.addEventListener('click', openCart);
  cartCloseBtn?.addEventListener('click', closeCart);
  cartOverlay?.addEventListener('click', closeCart);

  // --- Cart State Logic ---
  window.addToCart = function(itemId) {
    const dish = allMenuItems.find(i => i.id === itemId);
    if (!dish) return;

    const existing = cart.find(i => i.id === itemId);
    if (existing) {
      existing.quantity += 1;
    } else {
      cart.push({
        id: dish.id,
        name: dish.name,
        price: dish.price,
        image_url: dish.image_url,
        quantity: 1
      });
    }

    saveCart();
    renderCart();
    openCart();
  };

  window.changeQty = function(itemId, delta) {
    const item = cart.find(i => i.id === itemId);
    if (!item) return;

    item.quantity += delta;
    if (item.quantity <= 0) {
      cart = cart.filter(i => i.id !== itemId);
    }
    saveCart();
    renderCart();
  };

  function saveCart() {
    localStorage.setItem('luxury_restaurant_cart', JSON.stringify(cart));
    updateCartBadges();
  }

  function updateCartBadges() {
    const totalCount = cart.reduce((acc, item) => acc + item.quantity, 0);
    const badges = document.querySelectorAll('.cart-badge');
    badges.forEach(b => {
      b.textContent = totalCount;
      b.style.display = totalCount > 0 ? 'flex' : 'none';
    });
  }

  function renderCart() {
    const cartList = document.getElementById('cart-items-container');
    const subtotalEl = document.getElementById('cart-subtotal');
    const taxEl = document.getElementById('cart-tax');
    const totalEl = document.getElementById('cart-total');
    const checkoutBtn = document.getElementById('cart-checkout-btn');

    if (!cartList) return;

    if (cart.length === 0) {
      cartList.innerHTML = `
        <div class="cart-empty-state">
          <p style="font-family: var(--font-serif); font-size: 1.1rem; color: #fff; margin-bottom: 0.5rem;">Your Tasting Order is Empty</p>
          <p style="font-size: 0.85rem;">Select from our curated menu to assemble your private experience.</p>
        </div>
      `;
      if (subtotalEl) subtotalEl.textContent = '$0.00';
      if (taxEl) taxEl.textContent = '$0.00';
      if (totalEl) totalEl.textContent = '$0.00';
      if (checkoutBtn) checkoutBtn.disabled = true;
      return;
    }

    let subtotal = 0;
    cartList.innerHTML = cart.map(item => {
      const itemTotal = item.price * item.quantity;
      subtotal += itemTotal;
      return `
        <div class="cart-item">
          <div class="cart-item-info">
            <h4 class="cart-item-title">${item.name}</h4>
            <div class="cart-item-price">$${item.price.toFixed(2)} each</div>
          </div>
          <div class="qty-controls">
            <button class="qty-btn" onclick="window.changeQty(${item.id}, -1)">-</button>
            <span class="qty-val">${item.quantity}</span>
            <button class="qty-btn" onclick="window.changeQty(${item.id}, 1)">+</button>
          </div>
        </div>
      `;
    }).join('');

    const tax = subtotal * 0.085;
    const total = subtotal + tax;

    if (subtotalEl) subtotalEl.textContent = `$${subtotal.toFixed(2)}`;
    if (taxEl) taxEl.textContent = `$${tax.toFixed(2)}`;
    if (totalEl) totalEl.textContent = `$${total.toFixed(2)}`;
    if (checkoutBtn) checkoutBtn.disabled = false;
  }

  // --- Tip & Bill Breakdown in Order Modal ---
  function updateOrderModalTotals() {
    let subtotal = 0;
    cart.forEach(item => {
      subtotal += item.price * item.quantity;
    });

    const tax = subtotal * 0.085;
    const tipPercent = parseFloat(document.getElementById('order-tip-percent')?.value || '18');
    const tip = subtotal * (tipPercent / 100);
    const total = subtotal + tax + tip;

    const subEl = document.getElementById('modal-subtotal');
    const taxEl = document.getElementById('modal-tax');
    const tipEl = document.getElementById('modal-tip');
    const totEl = document.getElementById('modal-total');

    if (subEl) subEl.textContent = `$${subtotal.toFixed(2)}`;
    if (taxEl) taxEl.textContent = `$${tax.toFixed(2)}`;
    if (tipEl) tipEl.textContent = `$${tip.toFixed(2)}`;
    if (totEl) totEl.textContent = `$${total.toFixed(2)}`;
  }

  // Tip buttons event listeners
  const tipButtons = document.querySelectorAll('.tip-btn');
  tipButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      tipButtons.forEach(b => {
        b.classList.remove('active');
        b.style.background = 'transparent';
      });
      btn.classList.add('active');
      btn.style.background = 'rgba(212, 175, 55, 0.2)';
      const tipVal = btn.dataset.tip;
      const hiddenTip = document.getElementById('order-tip-percent');
      if (hiddenTip) hiddenTip.value = tipVal;
      updateOrderModalTotals();
    });
  });

  // Card input auto-format
  const cardInput = document.getElementById('order-card-number');
  cardInput?.addEventListener('input', (e) => {
    let val = e.target.value.replace(/\D/g, '').substring(0, 16);
    let formatted = val.match(/.{1,4}/g)?.join(' ') || val;
    e.target.value = formatted;
  });

  // --- Order Placement Modal & Form ---
  const checkoutBtn = document.getElementById('cart-checkout-btn');
  const orderModal = document.getElementById('order-modal');
  const orderCloseBtn = document.getElementById('order-close-btn');
  const orderForm = document.getElementById('order-form');

  checkoutBtn?.addEventListener('click', () => {
    closeCart();
    updateOrderModalTotals();
    orderModal?.classList.add('open');
  });

  orderCloseBtn?.addEventListener('click', () => {
    orderModal?.classList.remove('open');
  });

  orderForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const submitBtn = orderForm.querySelector('button[type="submit"]');
    if (submitBtn) submitBtn.disabled = true;

    let subtotal = 0;
    cart.forEach(item => { subtotal += item.price * item.quantity; });
    const tipPercent = parseFloat(document.getElementById('order-tip-percent')?.value || '18');
    const tipAmount = (subtotal * (tipPercent / 100)).toFixed(2);

    const payload = {
      customer_name: document.getElementById('order-name').value,
      email: document.getElementById('order-email').value,
      phone: document.getElementById('order-phone').value,
      order_type: document.getElementById('order-type').value,
      table_or_address: document.getElementById('order-location').value,
      notes: document.getElementById('order-notes').value,
      tip_amount: tipAmount,
      payment_method: 'Credit Card',
      card_number: document.getElementById('order-card-number')?.value || '4000 1234 5678 9010',
      items: cart
    };

    try {
      const res = await fetch('/api/order/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify(payload)
      });
      const data = await res.json();

      if (data.success) {
        // Clear cart
        cart = [];
        saveCart();
        renderCart();

        orderModal?.classList.remove('open');

        // Show Success Confirmation Modal with View Official Receipt link
        const receiptBtn = document.getElementById('view-receipt-btn');
        if (receiptBtn) {
          receiptBtn.href = `/order/${data.order_number}/receipt/`;
          receiptBtn.style.display = 'inline-flex';
        }

        showSuccessModal(
          `Payment Authorized • Order #${data.order_number}`,
          `Thank you, ${data.customer_name}. Payment of $${data.total.toFixed(2)} was charged to card ending in ${data.card_last4}. Your ${data.order_type} has been dispatched to our kitchen brigade.`
        );
        orderForm.reset();
      } else {
        alert(data.error || 'Failed to place order.');
      }
    } catch (err) {
      console.error(err);
      alert('Network error while placing order.');
    } finally {
      if (submitBtn) submitBtn.disabled = false;
    }
  });

  // --- Table Reservation Form Handling ---
  const reservationForm = document.getElementById('reservation-form');
  const dateInput = document.getElementById('res-date');
  if (dateInput) {
    const today = new Date().toISOString().split('T')[0];
    dateInput.min = today;
  }

  reservationForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = reservationForm.querySelector('button[type="submit"]');
    if (btn) btn.disabled = true;

    const payload = {
      customer_name: document.getElementById('res-name').value,
      email: document.getElementById('res-email').value,
      phone: document.getElementById('res-phone').value,
      date: document.getElementById('res-date').value,
      time_slot: document.getElementById('res-time').value,
      guests: document.getElementById('res-guests').value,
      seating_area: document.getElementById('res-seating').value,
      special_requests: document.getElementById('res-notes').value,
    };

    try {
      const res = await fetch('/api/reserve/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify(payload)
      });
      const data = await res.json();

      if (data.success) {
        showSuccessModal(
          `Reservation Confirmed: ${data.booking_code}`,
          `We look forward to welcoming you, ${data.customer_name}, on ${data.date} at ${data.time_slot} (${data.guests} guests, ${data.seating_area}).`
        );
        reservationForm.reset();
      } else {
        alert(data.error || 'Could not complete reservation.');
      }
    } catch (err) {
      console.error(err);
      alert('Error connecting to the reservation service.');
    } finally {
      if (btn) btn.disabled = false;
    }
  });

  // --- Success Modal Helper ---
  function showSuccessModal(title, message) {
    const modal = document.getElementById('success-modal');
    const titleEl = document.getElementById('success-modal-title');
    const msgEl = document.getElementById('success-modal-msg');

    if (titleEl) titleEl.textContent = title;
    if (msgEl) msgEl.textContent = message;
    modal?.classList.add('open');
  }

  // --- Dish Reviews & Tasting Notes Modal Logic ---
  const reviewModal = document.getElementById('dish-review-modal');
  const reviewCloseBtn = document.getElementById('dish-review-close-btn');
  const reviewForm = document.getElementById('dish-review-form');
  const starPicks = document.querySelectorAll('.star-pick');
  const reviewRatingInput = document.getElementById('review-rating-val');

  // Star Picker interaction
  function setStarRating(val) {
    if (reviewRatingInput) reviewRatingInput.value = val;
    starPicks.forEach(star => {
      const sVal = parseInt(star.dataset.val, 10);
      if (sVal <= val) {
        star.style.color = 'var(--gold-light)';
        star.style.opacity = '1';
      } else {
        star.style.color = '#4b5563';
        star.style.opacity = '0.6';
      }
    });
  }
  setStarRating(5);

  starPicks.forEach(star => {
    star.addEventListener('click', () => {
      const val = parseInt(star.dataset.val, 10);
      setStarRating(val);
    });
  });

  window.openDishReviews = async function(itemId) {
    const dish = allMenuItems.find(i => i.id === itemId);
    const dishIdInput = document.getElementById('review-dish-id');
    const dishNameEl = document.getElementById('modal-dish-name');
    const dishRatingEl = document.getElementById('modal-dish-rating');
    const dishCountEl = document.getElementById('modal-dish-count');
    const container = document.getElementById('modal-reviews-container');

    if (dishIdInput) dishIdInput.value = itemId;
    if (dishNameEl) dishNameEl.textContent = dish ? dish.name : 'Curated Dish';
    if (dishRatingEl) dishRatingEl.textContent = dish ? `★ ${dish.rating.toFixed(1)}` : '★ 5.0';
    if (container) container.innerHTML = '<p style="color: var(--text-muted); font-size: 0.9rem;">Fetching authentic tasting notes...</p>';

    reviewModal?.classList.add('open');

    try {
      const res = await fetch(`/api/dish/${itemId}/reviews/`);
      const data = await res.json();
      
      if (dishCountEl) dishCountEl.textContent = `(${data.reviews.length} Tasting Notes)`;
      if (dishRatingEl) dishRatingEl.textContent = `★ ${data.item.rating.toFixed(1)}`;

      if (data.reviews.length === 0) {
        container.innerHTML = `
          <div style="padding: 1.5rem; background: rgba(255,255,255,0.02); border-radius: 6px; text-align: center; color: var(--text-muted);">
            <p style="font-family: var(--font-serif); font-size: 1.05rem; color: #fff; margin-bottom: 0.25rem;">No Tasting Notes Yet</p>
            <p style="font-size: 0.85rem;">Be the inaugural patron to record a review for this creation below.</p>
          </div>
        `;
      } else {
        container.innerHTML = data.reviews.map(r => `
          <div style="background: rgba(10,12,16,0.5); border: 1px solid rgba(255,255,255,0.06); border-radius: 6px; padding: 1rem 1.25rem;">
            <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.25rem;">
              <span style="font-weight: 600; color: #fff; font-size: 0.92rem;">${r.author_name}</span>
              <span style="font-size: 0.78rem; color: var(--text-faint);">${r.date}</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.4rem; margin-bottom: 0.4rem;">
              <span style="color: var(--gold-light); font-size: 0.9rem;">${'★'.repeat(r.rating)}${'☆'.repeat(5 - r.rating)}</span>
              ${r.headline ? `<strong style="font-size: 0.88rem; color: #f3f4f6;">${r.headline}</strong>` : ''}
            </div>
            <p style="font-size: 0.85rem; color: var(--text-muted); line-height: 1.5; margin: 0;">${r.comment}</p>
          </div>
        `).join('');
      }
    } catch (err) {
      console.error(err);
      container.innerHTML = '<p style="color: #f87171; font-size: 0.85rem;">Failed to load reviews.</p>';
    }
  };

  reviewCloseBtn?.addEventListener('click', () => {
    reviewModal?.classList.remove('open');
  });

  reviewForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const submitBtn = reviewForm.querySelector('button[type="submit"]');
    if (submitBtn) submitBtn.disabled = true;

    const itemId = parseInt(document.getElementById('review-dish-id')?.value, 10);
    const payload = {
      item_id: itemId,
      rating: parseInt(document.getElementById('review-rating-val')?.value || '5', 10),
      author_name: document.getElementById('review-author')?.value,
      headline: document.getElementById('review-headline')?.value,
      comment: document.getElementById('review-comment')?.value,
    };

    try {
      const res = await fetch('/api/dish/review/submit/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify(payload)
      });
      const data = await res.json();

      if (data.success) {
        // Update local item rating
        const targetDish = allMenuItems.find(i => i.id === itemId);
        if (targetDish) {
          targetDish.rating = data.new_rating;
          renderMenu();
        }

        // Prepend review into modal
        const container = document.getElementById('modal-reviews-container');
        const dishCountEl = document.getElementById('modal-dish-count');
        const dishRatingEl = document.getElementById('modal-dish-rating');

        if (dishRatingEl) dishRatingEl.textContent = `★ ${data.new_rating.toFixed(1)}`;
        if (dishCountEl) dishCountEl.textContent = `(${data.reviews_count} Tasting Notes)`;

        const newReviewHTML = `
          <div style="background: rgba(10,12,16,0.5); border: 1px solid var(--border-subtle); border-radius: 6px; padding: 1rem 1.25rem;">
            <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.25rem;">
              <span style="font-weight: 600; color: #fff; font-size: 0.92rem;">${data.review.author_name}</span>
              <span style="font-size: 0.78rem; color: var(--gold-light);">Just now</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.4rem; margin-bottom: 0.4rem;">
              <span style="color: var(--gold-light); font-size: 0.9rem;">${'★'.repeat(data.review.rating)}${'☆'.repeat(5 - data.review.rating)}</span>
              ${data.review.headline ? `<strong style="font-size: 0.88rem; color: #f3f4f6;">${data.review.headline}</strong>` : ''}
            </div>
            <p style="font-size: 0.85rem; color: var(--text-muted); line-height: 1.5; margin: 0;">${data.review.comment}</p>
          </div>
        `;

        if (container) {
          if (container.querySelector('p')) {
            container.innerHTML = newReviewHTML;
          } else {
            container.insertAdjacentHTML('afterbegin', newReviewHTML);
          }
        }

        document.getElementById('review-headline').value = '';
        document.getElementById('review-comment').value = '';
        setStarRating(5);
        alert(data.message);
      } else {
        alert(data.error || 'Failed to submit review.');
      }
    } catch (err) {
      console.error(err);
      alert('Network error submitting tasting note.');
    } finally {
      if (submitBtn) submitBtn.disabled = false;
    }
  });

  // Initialize
  updateCartBadges();
  renderCart();
  loadMenuData();
});

