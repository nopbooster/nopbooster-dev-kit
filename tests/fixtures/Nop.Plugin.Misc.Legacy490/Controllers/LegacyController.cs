using FluentValidation.AspNetCore;
using Microsoft.AspNetCore.Mvc;
using Nop.Core;
using Nop.Core.Domain.News;
using Nop.Services.Logging;
using Nop.Services.News;
using Nop.Web.Framework.Controllers;
using Nop.Web.Framework.Themes;

namespace Nop.Plugin.Misc.Legacy490.Controllers;

public class LegacyController : BasePluginController
{
    private readonly ILogger _logger;
    private readonly INewsService _newsService;
    private readonly IThemeContext _themeContext;
    private readonly IWebHelper _webHelper;

    public LegacyController(ILogger logger, INewsService newsService, IThemeContext themeContext, IWebHelper webHelper)
    {
        _logger = logger;
        _newsService = newsService;
        _themeContext = themeContext;
        _webHelper = webHelper;
    }

    public async Task<IActionResult> Latest()
    {
        var news = await _newsService.GetAllNewsAsync();
        _logger.Information("Listed news for " + _webHelper.GetThisPageUrl(false));
        return View(news);
    }

    public IActionResult Topic()
    {
        return Redirect(Url.RouteTopicUrl("shippinginfo"));
    }
}
