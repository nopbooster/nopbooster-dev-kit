using Nop.Core.Domain.Catalog;
using Nop.Services.Catalog;
using Nop.Services.Cms;
using Nop.Services.Configuration;
using Nop.Services.Localization;
using Nop.Services.Messages;
using Nop.Web.Framework.Infrastructure;

namespace Nop.Plugin.Misc.Legacy490.Services;

public class LegacyService
{
    private readonly ILocalizationService _localizationService;
    private readonly IMessageTokenProvider _messageTokenProvider;
    private readonly IPriceFormatter _priceFormatter;
    private readonly ISettingService _settingService;

    public LegacyService(ILocalizationService localizationService, IMessageTokenProvider messageTokenProvider,
        IPriceFormatter priceFormatter, ISettingService settingService)
    {
        _localizationService = localizationService;
        _messageTokenProvider = messageTokenProvider;
        _priceFormatter = priceFormatter;
        _settingService = settingService;
    }

    public Task<IList<string>> GetWidgetZonesAsync()
    {
        return Task.FromResult<IList<string>>(new List<string> { PublicWidgetZones.HomepageBeforeNews, PublicWidgetZones.ProductDetailsTop });
    }

    public async Task<string> BasePriceAsync(Product product)
    {
        _settingService.ClearCache();
        return await _priceFormatter.FormatBasePriceAsync(product, product.Price, null);
    }

    public async Task<IEnumerable<string>> TokensAsync()
    {
        return await _messageTokenProvider.GetListOfAllowedTokensAsync(new List<string> { "Store" });
    }
}
