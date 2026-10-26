// Global variable to track the ticket being edited
let editTicketId = null;

// Chart.js chart instances
let categoryChart = null;
let priorityChart = null;

// DOM elements
const ticketForm = document.getElementById('ticket-form');
const formMessage = document.getElementById('form-message');
const ticketsTableBody = document.querySelector('#tickets-table tbody');

// Statistic elements
const totalTicketsEl = document.getElementById('total-tickets');
const openTicketsEl = document.getElementById('open-tickets');
const resolvedTicketsEl = document.getElementById('resolved-tickets');
const highPriorityTicketsEl = document.getElementById('high-priority-tickets');

// Chat elements
const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');
const chatMessages = document.getElementById('chat-messages');

// Fetch and display tickets and analytics on page load
document.addEventListener('DOMContentLoaded', () => {
    fetchTickets();
    fetchAnalytics();
});

// Handle ticket form submission
ticketForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    formMessage.textContent = '';
    formMessage.className = '';

    const title = document.getElementById('title').value.trim();
    const description = document.getElementById('description').value.trim();
    const category = document.getElementById('category').value;
    const priority = document.getElementById('priority').value;
    const status = document.getElementById('status').value;

    // Basic validation
    if (!title || !description || !category || !priority) {
        showMessage('Please fill in all required fields', 'error');
        return;
    }

    const ticketData = {
        title,
        description,
        category,
        priority,
        status
    };

    try {
        if (editTicketId === null) {
            // Create new ticket
            const response = await fetch('/api/tickets', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(ticketData)
            });

            if (response.ok) {
                showMessage('Ticket created successfully', 'success');
                ticketForm.reset();
                await fetchTickets();
                await fetchAnalytics(); // Update analytics after creating a ticket
            } else {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to create ticket');
            }
        } else {
            // Update existing ticket
            const response = await fetch(`/api/tickets/${editTicketId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(ticketData)
            });

            if (response.ok) {
                showMessage('Ticket updated successfully', 'success');
                ticketForm.reset();
                editTicketId = null;
                // Change submit button text back
                const submitButton = ticketForm.querySelector('button[type="submit"]');
                submitButton.textContent = 'Submit Ticket';
                await fetchTickets();
                await fetchAnalytics(); // Update analytics after updating a ticket
            } else {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to update ticket');
            }
        }
    } catch (error) {
        showMessage(error.message, 'error');
    }
});

// Handle chat form submission
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const message = chatInput.value.trim();
    if (!message) {
        return;
    }
    
    // Disable input and show sending state
    chatInput.disabled = true;
    chatForm.querySelector('button[type="submit"]').disabled = true;
    
    // Add user message to chat
    addChatMessage(message, 'user');
    
    // Clear input
    chatInput.value = '';
    
    try {
        // Send message to backend
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });

        if (response.ok) {
            const data = await response.json();
            // Add bot response to chat
            addChatMessage(data.response, 'bot');
        } else {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to get response from AI assistant');
        }
    } catch (error) {
        // Add error message to chat
        addChatMessage("I'm sorry, I encountered an error while processing your request. Please try again.", 'bot');
        console.error('Error in chat:', error);
    } finally {
        // Re-enable input
        chatInput.disabled = false;
        chatForm.querySelector('button[type="submit"]').disabled = false;
        chatInput.focus();
    }
});

// Fetch tickets from the API and update the table
async function fetchTickets() {
    try {
        const response = await fetch('/api/tickets');
        if (!response.ok) {
            throw new Error('Failed to fetch tickets');
        }
        const tickets = await response.json();
        renderTicketsTable(tickets);
    } catch (error) {
        showMessage(error.message, 'error');
        console.error('Error fetching tickets:', error);
    }
}

// Fetch analytics from the API and update statistic cards and charts
async function fetchAnalytics() {
    try {
        const response = await fetch('/api/analytics');
        if (!response.ok) {
            throw new Error('Failed to fetch analytics');
        }
        const stats = await response.json();
        updateStatistics(stats);
        updateCharts(stats);
    } catch (error) {
        showMessage(error.message, 'error');
        console.error('Error fetching analytics:', error);
    }
}

// Render the tickets table
function renderTicketsTable(tickets) {
    ticketsTableBody.innerHTML = '';

    if (tickets.length === 0) {
        ticketsTableBody.innerHTML = '<tr><td colspan="7">No tickets found</td></tr>';
        return;
    }

    tickets.forEach(ticket => {
        const tr = document.createElement('tr');

        tr.innerHTML = `
            <td>${ticket.id}</td>
            <td>${ticket.title}</td>
            <td>${ticket.category}</td>
            <td>${ticket.priority}</td>
            <td>${ticket.status}</td>
            <td>${ticket.created_at}</td>
            <td>
                <button class="edit-btn" data-id="${ticket.id}">Edit</button>
                <button class="delete-btn" data-id="${ticket.id}">Delete</button>
            </td>
        `;

        ticketsTableBody.appendChild(tr);
    });

    // Add event listeners to edit and delete buttons
    document.querySelectorAll('.edit-btn').forEach(button => {
        button.addEventListener('click', handleEditClick);
    });

    document.querySelectorAll('.delete-btn').forEach(button => {
        button.addEventListener('click', handleDeleteClick);
    });
}

// Handle edit button click
async function handleEditClick(e) {
    const ticketId = parseInt(e.target.dataset.id);
    try {
        const response = await fetch(`/api/tickets/${ticketId}`);
        if (!response.ok) {
            throw new Error('Failed to fetch ticket for editing');
        }
        const ticket = await response.json();

        // Populate the form with ticket data
        document.getElementById('title').value = ticket.title;
        document.getElementById('description').value = ticket.description;
        document.getElementById('category').value = ticket.category;
        document.getElementById('priority').value = ticket.priority;
        document.getElementById('status').value = ticket.status;

        // Set editTicketId and change button text
        editTicketId = ticketId;
        const submitButton = ticketForm.querySelector('button[type="submit"]');
        submitButton.textContent = 'Update Ticket';

        // Scroll to form
        ticketForm.scrollIntoView({ behavior: 'smooth' });
    } catch (error) {
        showMessage(error.message, 'error');
        console.error('Error fetching ticket for edit:', error);
    }
}

// Handle delete button click
async function handleDeleteClick(e) {
    if (!confirm('Are you sure you want to delete this ticket?')) {
        return;
    }

    const ticketId = parseInt(e.target.dataset.id);
    try {
        const response = await fetch(`/api/tickets/${ticketId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showMessage('Ticket deleted successfully', 'success');
            await fetchTickets();
            await fetchAnalytics(); // Update analytics after deleting a ticket
        } else {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to delete ticket');
        }
    } catch (error) {
        showMessage(error.message, 'error');
        console.error('Error deleting ticket:', error);
    }
}

// Show message in the form message area
function showMessage(message, type) {
    formMessage.textContent = message;
    formMessage.className = type; // 'success' or 'error'
    // Clear message after 3 seconds
    setTimeout(() => {
        formMessage.textContent = '';
        formMessage.className = '';
    }, 3000);
}

// Add a message to the chat window
function addChatMessage(message, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    messageDiv.textContent = message;
    chatMessages.appendChild(messageDiv);
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Update statistic cards with data from analytics
function updateStatistics(stats) {
    totalTicketsEl.textContent = stats.total_tickets;
    openTicketsEl.textContent = stats.open_tickets;
    resolvedTicketsEl.textContent = stats.resolved_tickets;
    highPriorityTicketsEl.textContent = stats.high_priority_tickets;
}

// Update Chart.js charts with data from analytics
function updateCharts(stats) {
    const categoryData = stats.tickets_by_category;
    const priorityData = stats.tickets_by_priority;

    // Update or create category chart (pie chart)
    const categoryCtx = document.getElementById('category-chart').getContext('2d');
    if (categoryChart) {
        categoryChart.data.labels = Object.keys(categoryData);
        categoryChart.data.datasets[0].data = Object.values(categoryData);
        categoryChart.update();
    } else {
        categoryChart = new Chart(categoryCtx, {
            type: 'pie',
            data: {
                labels: Object.keys(categoryData),
                datasets: [{
                    data: Object.values(categoryData),
                    backgroundColor: [
                        '#FF6384',
                        '#36A2EB',
                        '#FFCE56',
                        '#4BC0C0',
                        '#9966FF',
                        '#FF9F40'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    title: {
                        display: true,
                        text: 'Tickets by Category'
                    }
                }
            }
        });
    }

    // Update or create priority chart (bar chart)
    const priorityCtx = document.getElementById('priority-chart').getContext('2d');
    if (priorityChart) {
        priorityChart.data.labels = Object.keys(priorityData);
        priorityChart.data.datasets[0].data = Object.values(priorityData);
        priorityChart.update();
    } else {
        priorityChart = new Chart(priorityCtx, {
            type: 'bar',
            data: {
                labels: Object.keys(priorityData),
                datasets: [{
                    label: 'Tickets by Priority',
                    data: Object.values(priorityData),
                    backgroundColor: [
                        '#28a745',
                        '#ffc107',
                        '#fd7e14',
                        '#dc3545',
                        '#6f42c1'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Tickets by Priority'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                }
            }
        });
    }
}