using Microsoft.AspNetCore.Mvc;
using Nop.Services.Security;
using Nop.Web.Framework.Controllers;

namespace Nop.Plugin.Misc.Legacy.Controllers;

public class LegacyController : BasePluginController
{
    protected readonly IPermissionService _permissionService;

    public LegacyController(IPermissionService permissionService) => _permissionService = permissionService;

    public async Task<IActionResult> Configure()
    {
        if (!await _permissionService.AuthorizeAsync(StandardPermissionProvider.ManagePlugins))
            return AccessDeniedView();

        return View("~/Plugins/Misc.Legacy/Views/Configure.cshtml");
    }
}
