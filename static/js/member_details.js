// --------- Tab functionality ----------
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        // Remove active class from all tabs
        document.querySelectorAll('.tab-btn').forEach(b => {
            b.classList.remove('tab-active');
            b.classList.add('text-gray-600');
        });

        // Add active class to clicked tab
        btn.classList.add('tab-active');
        btn.classList.remove('text-gray-600');

        // Hide all tab contents
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.add('hidden');
        });

        // Show selected tab content
        document.getElementById(btn.dataset.tab).classList.remove('hidden');
    });
});


// ---------- Meal edit functionality -------------
document.querySelectorAll('.meal-edit-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const meal_id = this.closest('.grid').querySelector('.meal-id').textContent;
        const date = this.closest('.grid').querySelector('.date').textContent;
        const breakfast = this.closest('.grid').querySelector('.breakfast').textContent;
        const lunch = this.closest('.grid').querySelector('.lunch').textContent;
        const dinner = this.closest('.grid').querySelector('.dinner').textContent;

        openMealModal(meal_id, date, breakfast, lunch, dinner);
    });
});


// Open modal with current values
// arr args are as string
function openMealModal(meal_id, date, breakfast, lunch, dinner) {
    // Set modal title
    document.getElementById('modalDate').textContent = date;

    // Set current values
    document.getElementById('meal_id').value = meal_id;
    document.getElementById('edit_breakfast').value = breakfast;
    document.getElementById('edit_lunch').value = lunch;
    document.getElementById('edit_dinner').value = dinner;

    // Show modal
    document.getElementById('mealEditModal').classList.remove('hidden');
}

// Close modal
document.getElementById('closeMealModal').addEventListener('click', () => {
    document.getElementById('mealEditModal').classList.add('hidden');
});


// -------- Approve grocery ------------
document.querySelectorAll('.grocery-approve').forEach(btn => {
    btn.addEventListener('click', function() {
        const item = this.closest('.grid').querySelector('.grocery-name').textContent;

        this.classList.remove('fa-check');
        this.classList.add('fa-check-circle');
        this.parentElement.classList.add('text-green-600');

        alert(`Approved: ${item}`);
    });
});


// ----------- Delete groceries ------------
document.querySelectorAll('.grocery-delete').forEach(btn => {
    btn.addEventListener('click', function() {
        const item = this.closest('.grid').querySelector('.grocery-name').textContent;

        if (confirm(`Delete "${item}"?`)) {
            this.closest('.grid').remove();
        }
    });
});




// ---------- Grocery edit functionality ---------------
document.querySelectorAll('.grocery-edit').forEach(btn => {
    btn.addEventListener('click', function() {
        const grocery_id = this.closest('.grid').querySelector('.grocery-id').textContent;
        const date = this.closest('.grid').querySelector('.date').textContent;
        const itemName = this.closest('.grid').querySelector('.grocery-name').textContent;
        const quantity = this.closest('.grid').querySelector('.quantity').textContent;
        const cost = this.closest('.grid').querySelector('.grocery-cost').textContent;

        openGroceryModal(grocery_id, date, itemName, quantity, cost);
    });
});


// Open grocery modal with current values
function openGroceryModal(grocery_id, date, itemName, quantity, cost) {
    // Set current values
    document.getElementById('grocery_id').value = grocery_id;
    document.getElementById('grocery-date').textContent = date;
    document.getElementById('edit_grocery_name').value = itemName;
    document.getElementById('edit_grocery_quantity').value = quantity || '';
    document.getElementById('edit_grocery_cost').value = cost;

    // Show modal
    document.getElementById('groceryEditModal').classList.remove('hidden');
}

// Close grocery modal
document.getElementById('closeGroceryModal').addEventListener('click', () => {
    document.getElementById('groceryEditModal').classList.add('hidden');
});




// ---------- Open add grocery modal --------------
document.getElementById('add-grocery-btn').addEventListener('click', () => {
    // Set today's date as default
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('groceryDate').value = today;

    // Show modal
    document.getElementById('addGroceryModal').classList.remove('hidden');
});


// Close add grocery modal
document.getElementById('closeAddGroceryModal').addEventListener('click', () => {
    document.getElementById('addGroceryModal').classList.add('hidden');
    // Reset form (optional)
    document.getElementById('addGroceryForm').reset();
});
