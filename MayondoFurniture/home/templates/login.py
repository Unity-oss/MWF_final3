from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from home.models import Sale


# Create your views here.
def landingPage(request):
    return render(request, "index.html",)

def createAccount(request):
    return render(request, "account.html")
def loginPage(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if user.groups.filter(name="Manager").exists():
                return redirect("dashboard")
            elif user.groups.filter(name="Employee").exists():
                return redirect("dashboard_employee")
            else:
                return redirect("dashboard")  # fallback
        else:
            return render(request, "login.html", {"error": "Invalid username or password"})

    return render(request, "login.html")

@login_required
def dashBoard(request):
    context = {
        "username": "Unity Busingye",
        "email": "unity@mwf.org",
    }
    return render(request, "dashboard.html", context)
@login_required
def dashEmployee(request):
    return render(request, "dash_employee.html")
@login_required
def saleRecord(request):
    if request.method == 'POST':
        form_data = request.POST
        sent_customerName = form_data.get('customer_name')
        sent_productName = form_data.get('product_name')
        sent_productType = form_data.get('product_type')
        sent_quantity = form_data.get('quantity')
        sent_date = form_data.get('date')
        sent_paymentType = form_data.get('payment_type')
        sent_saleAgent = form_data.get('sales_agent')
        sent_transportRequired = form_data.get('transport_required')


             # option 1
        new_item = Sale()
        new_item.customer_name = sent_customerName
        new_item.product_name = sent_productName
        new_item.product_type = sent_productType
        new_item.quantity = sent_quantity
        new_item.date = sent_date
        new_item.payment_type = sent_paymentType
        new_item.sales_agent = sent_saleAgent
        new_item.transport_required = sent_transportRequired
        new_item.save()
        return redirect('/')
    
    return render(request, 'sales.html')
@login_required
def saleReport(request):
    all_Sale = Sale.objects.all()

    context = {
        "sales": all_Sale
    }
    return render(request, "sales_report.html", context)
def logoutPage(request):
    logout(request)
    return redirect('login')


class Profile(models.Model):
    ROLE_CHOICES = (
        ('manager', 'Manager'),
        ('employee', 'Employee')
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES,default='employee')

    from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

 <script>
        // Initialize Chart.js with Cordes styling
        const ctx = document.getElementById('revenueChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Revenue',
                    data: [25000, 32000, 28000, 35000, 42000, 48000],
                    borderColor: '#1e40af',
                    backgroundColor: 'rgba(30, 64, 175, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#1e40af',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: '#6b7280'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: '#f3f4f6'
                        },
                        ticks: {
                            color: '#6b7280',
                            callback: function(value) {
                                return ' + value.toLocaleString();
                            }
                        }
                    }
                },
                elements: {
                    point: {
                        hoverRadius: 8
                    }
                }
            }
        });

        // Add some interactive functionality
        document.addEventListener('DOMContentLoaded', function() {
            // Sidebar navigation active state
            const navLinks = document.querySelectorAll('nav a');
            navLinks.forEach(link => {
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    navLinks.forEach(l => l.classList.remove('bg-gray-700', 'text-white'));
                    navLinks.forEach(l => l.classList.add('text-gray-300'));
                    this.classList.add('bg-gray-700', 'text-white');
                    this.classList.remove('text-gray-300');
                });
            });

            // Set dashboard as active by default
            navLinks[0].classList.add('bg-gray-700', 'text-white');
            navLinks[0].classList.remove('text-gray-300');

            // Notification bell animation
            const bellIcon = document.querySelector('.fa-bell');
            if (bellIcon) {
                setInterval(() => {
                    bellIcon.classList.add('animate-pulse');
                    setTimeout(() => {
                        bellIcon.classList.remove('animate-pulse');
                    }, 1000);
                }, 5000);
            }

            // Stats cards hover effects
            const statsCards = document.querySelectorAll('.hover\\:shadow-md');
            statsCards.forEach(card => {
                card.addEventListener('mouseenter', function() {
                    this.style.transform = 'translateY(-2px)';
                });
                card.addEventListener('mouseleave', function() {
                    this.style.transform = 'translateY(0)';
                });
            });
        });
    </script>


<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MWF</title>
    <link rel="stylesheet" href="../static/stock-header.css">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
  <header class="main-header">
      <div class="logo">
        <h1>Stock Records</h1>
      </div>
      <nav class="nav-bar">
        <ul>
          <li><a href="/">login</a></li>
          <li><a href="/dashboard">Dashboard</a></li>
          <li><a href="/stock">Stock</a></li>
          <li><a href="/saleRecord">Sales</a></li>
          <li><a href="/report">Reports</a></li>
          <li><a href="/logout" class="Logout">Logout</a></li>
        </ul>
      </nav>
    </header>
    <section class="report_table">
          <form action="" method="post">
            <table
              class="table table-striped table-bordered table-light table-hover table-bordered"
            >
              <thead>
                <tr>
                  <th scope="col">Product Name</th>
                  <th scope="col">Cost Price</th>
                  <th scope="col">Product Price</th>
                  <th scope="col">Quantity</th>
                  <th scope="col">Supplier Name</th>
                  <th scope="col">Quality</th>
                  <th scope="col">Color</th>
                  <th scope="col">Measurements</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <th scope="row">1</th>
                  <td></td>
                  <td></td>
                  <td></td>
                  <td></td>
                  <td></td>
                  <td></td>
                  <td></td>
                </tr>
                <tr>
                  <th scope="row">2</th>
                  <td></td>
                  <td></td>
                  <td></td>
                  <td></td>
                  <td></td>
                  <td></td>
                  <td></td>
                </tr>
                <tr>
                  <th scope="row">3</th>
                  <td></td>
                  <td></td>
                  <td></td>
                  <td></td>
                  <td></td>
                  <td></td>
                  <td></td>
                </tr>
              </tbody>
            </table>
          </form>
        </section>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
