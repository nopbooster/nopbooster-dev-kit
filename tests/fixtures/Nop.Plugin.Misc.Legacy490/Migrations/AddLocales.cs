using FluentMigrator;
using Nop.Core.Infrastructure;
using Nop.Data.Migrations;
using Nop.Services.Localization;
using Nop.Web.Framework.Extensions;

namespace Nop.Plugin.Misc.Legacy490.Migrations;

[NopMigration("2025/10/01 10:00:00", "Misc.Legacy490 locales", MigrationProcessType.Update)]
public class AddLocales : MigrationBase
{
    public override void Up()
    {
        var (languageId, _) = this.GetLanguageData();
        var localizationService = EngineContext.Current.Resolve<ILocalizationService>();
        localizationService.AddOrUpdateLocaleResource(new Dictionary<string, string>
        {
            ["Plugins.Misc.Legacy490.Field"] = "Field",
        }, languageId);
    }

    public override void Down()
    {
    }
}
