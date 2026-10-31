using Nop.Services.Catalog;
using Nop.Services.Payments;
using Nop.Services.Shipping;

namespace Nop.Plugin.Misc.Legacy.Services;

public class LegacyService
{
    protected readonly IProductService _productService;
    protected readonly IShippingService _shippingService;
    protected readonly IPaymentService _paymentService;

    public LegacyService(IProductService productService, IShippingService shippingService, IPaymentService paymentService)
    {
        _productService = productService;
        _shippingService = shippingService;
        _paymentService = paymentService;
    }

    public async Task RunAsync(Nop.Core.Domain.Orders.Order order)
    {
        var reviews = await _productService.GetAllProductReviewsAsync(approved: true);
        var warehouse = await _shippingService.GetWarehouseByIdAsync(1);
        var methods = await _shippingService.GetAllShippingMethodsAsync();
        var values = _paymentService.DeserializeCustomValues(order);
    }
}
