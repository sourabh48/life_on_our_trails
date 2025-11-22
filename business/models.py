from django.conf import settings
from django.db import models
from django.utils.text import slugify

User = settings.AUTH_USER_MODEL


class BusinessCategory(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True, blank=True)
    icon_class = models.CharField(
        max_length=80,
        blank=True,
        help_text="Optional CSS icon class (e.g. 'fa fa-wrench').",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Business categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug = base
            counter = 1
            while BusinessCategory.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Business(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="businesses",
    )
    category = models.ForeignKey(
        BusinessCategory,
        on_delete=models.PROTECT,
        related_name="businesses",
    )

    name = models.CharField(max_length=140)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    tagline = models.CharField(max_length=180, blank=True)
    description = models.TextField(blank=True)

    cover_image = models.ImageField(
        upload_to="business/covers/",
        blank=True,
        null=True,
    )

    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=32, blank=True)
    website_url = models.URLField(blank=True)

    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(
        default=False,
        help_text="Admin must approve before public listing.",
    )
    is_locked = models.BooleanField(
        default=False,
        help_text="If locked, business is hidden even if approved.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug = base
            counter = 1
            while Business.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def is_visible_public(self) -> bool:
        """
        Used by views: only show to public when business is on, approved and not locked.
        """
        return self.is_active and self.is_approved and not self.is_locked

    @property
    def primary_city(self):
        loc = self.locations.filter(is_active=True).first()
        return loc.city if loc else ""


class BusinessLocation(models.Model):
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="locations",
    )

    label = models.CharField(
        max_length=80,
        blank=True,
        help_text="Optional label (e.g. 'Head office', 'Workshop').",
    )
    address_line1 = models.CharField(max_length=200)
    address_line2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=80)
    state = models.CharField(max_length=80, blank=True)
    pincode = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=80, default="India")

    google_maps_url = models.URLField(
        blank=True,
        help_text="Paste full Google Maps link here. We'll redirect user to this URL.",
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["city", "label"]

    def __str__(self):
        return f"{self.business.name} - {self.city}"


class BusinessService(models.Model):
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="services",
    )

    name = models.CharField(max_length=140)
    description = models.TextField(blank=True)
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Optional starting price.",
    )
    unit_label = models.CharField(
        max_length=40,
        blank=True,
        help_text="e.g. 'per day', 'per sq.ft', 'per service'",
    )
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self):
        return f"{self.business.name} - {self.name}"


class BusinessWorkImage(models.Model):
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="work_images",
    )
    image = models.ImageField(upload_to="business/work/")
    caption = models.CharField(max_length=160, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.business.name} work image"


class QuoteRequest(models.Model):
    class Status(models.TextChoices):
        NEW = "NEW", "New"
        IN_REVIEW = "IN_REVIEW", "In review"
        QUOTED = "QUOTED", "Quoted"
        ACCEPTED = "ACCEPTED", "Accepted"
        REJECTED = "REJECTED", "Rejected"
        CANCELLED = "CANCELLED", "Cancelled"

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="quotes",
    )
    customer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quotes",
    )

    full_name = models.CharField(max_length=140)
    email = models.EmailField()
    phone = models.CharField(max_length=32, blank=True)
    additional_details = models.TextField(blank=True)

    location = models.ForeignKey(
        BusinessLocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quotes",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
    )
    quoted_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
    )
    owner_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Quote {self.id} for {self.business.name}"


class QuoteServiceItem(models.Model):
    quote = models.ForeignKey(
        QuoteRequest,
        on_delete=models.CASCADE,
        related_name="items",
    )
    service = models.ForeignKey(
        BusinessService,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quote_items",
    )
    custom_label = models.CharField(
        max_length=160,
        blank=True,
        help_text="If no service linked, use this label.",
    )
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.display_name} (Quote {self.quote_id})"

    @property
    def display_name(self):
        if self.service:
            return self.service.name
        return self.custom_label or "Item"
