using Nop.Services.Plugins;
using Nop.Web.Framework.Menu;

namespace Nop.Plugin.Misc.Legacy;

public class LegacyPlugin : BasePlugin, IAdminMenuPlugin, IMiscPlugin
{
    public Task ManageSiteMapAsync(SiteMapNode rootNode)
    {
        rootNode.ChildNodes.Add(new SiteMapNode { SystemName = "Misc.Legacy", Title = "Legacy" });
        return Task.CompletedTask;
    }
}
