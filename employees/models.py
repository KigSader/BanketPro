from django.db import models


class Employee(models.Model):
    full_name = models.CharField('ФИО', max_length=200)
    phone = models.CharField('Телефон', max_length=50, blank=True)
    position = models.CharField('Должность', max_length=100, blank=True)
    hourly_rate = models.DecimalField('Ставка/час', max_digits=10, decimal_places=2, default=0)
    category = models.CharField('Категория', max_length=100, blank=True)
    contract = models.FileField('Договор', upload_to='employees/contracts/', blank=True, null=True)
    passport = models.FileField('Паспорт', upload_to='employees/passports/', blank=True, null=True)
    med_book = models.FileField('Мед. книжка', upload_to='employees/med/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


class Timesheet(models.Model):
    week_start = models.DateField('Начало недели (Пн)')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='timesheets')

    class Meta:
        unique_together = ('week_start', 'employee')


class TimesheetEntry(models.Model):
    timesheet = models.ForeignKey(Timesheet, on_delete=models.CASCADE, related_name='entries')
    date = models.DateField()
    hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)


class PayrollSettings(models.Model):
    kitchen_percent = models.DecimalField('Кухня, %', max_digits=5, decimal_places=2, default=4)
    service_percent = models.DecimalField('Сервис, %', max_digits=5, decimal_places=2, default=6)
