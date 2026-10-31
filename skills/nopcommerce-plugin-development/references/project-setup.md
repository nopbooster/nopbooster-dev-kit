# Project setup: .csproj, plugin.json, plugin class

## .csproj for 4.90

Place the project at `src/Plugins/Nop.Plugin.{Group}.{Name}/` and add it to `NopCommerce.sln` (solution folder `Plugins`). This matches the 4.90.8 core plugins:

```xml
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <TargetFramework>net9.0</TargetFramework>
    <Copyright>Copyright © {Company}</Copyright>
    <Company>{Company}</Company>
    <Authors>{Company}</Authors>
    <PackageProjectUrl>{https://your-site}</PackageProjectUrl>
    <OutputPath>$(SolutionDir)\Presentation\Nop.Web\Plugins\{Group}.{Name}</OutputPath>
    <OutDir>$(OutputPath)</OutDir>
    <!-- true only if the plugin references NuGet packages that core does not already ship -->
    <CopyLocalLockFileAssemblies>false</CopyLocalLockFileAssemblies>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>

  <ItemGroup>
    <None Remove="logo.png" />
    <None Remove="plugin.json" />
    <None Remove="Views\Configure.cshtml" />
    <None Remove="Views\_ViewImports.cshtml" />
  </ItemGroup>

  <ItemGroup>
    <Content Include="logo.png">
      <CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory>
    </Content>
    <Content Include="plugin.json">
      <CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory>
    </Content>
    <Content Include="Views\Configure.cshtml">
      <CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory>
    </Content>
    <Content Include="Views\_ViewImports.cshtml">
      <CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory>
    </Content>
  </ItemGroup>

  <ItemGroup>
    <ProjectReference Include="$(SolutionDir)\Presentation\Nop.Web\Nop.Web.csproj" />
    <ClearPluginAssemblies Include="$(SolutionDir)\Build\ClearPluginAssemblies.proj" />
  </ItemGroup>

  <!-- Runs after Build: removes DLLs that core already provides from the plugin folder -->
  <Target Name="NopTarget" AfterTargets="Build">
    <MSBuild Projects="@(ClearPluginAssemblies)" Properties="PluginPath=$(OutDir)" Targets="NopClear" />
  </Target>

</Project>
```

Every new `.cshtml` view, static file (js/css/images) and `logo.png` needs its own `<Content … CopyToOutputDirectory>` entry, or it will be missing at runtime.

**Because paths use `$(SolutionDir)`, build from the solution** (`dotnet build src/NopCommerce.sln` or Visual Studio). Building the `.csproj` alone leaves `$(SolutionDir)` empty; if that is needed, pass `-p:SolutionDir=<path-to-src>/`.

### Differences in older versions

4.70 used relative paths and net8.0:

```xml
<TargetFramework>net8.0</TargetFramework>
<OutputPath>..\..\Presentation\Nop.Web\Plugins\{Group}.{Name}</OutputPath>
<ProjectReference Include="..\..\Presentation\Nop.Web\Nop.Web.csproj" />
<ClearPluginAssemblies Include="$(MSBuildProjectDirectory)\..\..\Build\ClearPluginAssemblies.proj" />
<MSBuild Projects="@(ClearPluginAssemblies)" Properties="PluginPath=$(MSBuildProjectDirectory)\$(OutDir)" Targets="NopClear" />
```

4.80 and 4.90 both use the `$(SolutionDir)` layout above with `net9.0`; the switch from relative paths happened in 4.80. Core plugins also switched `logo.jpg` → `logo.png` in 4.90 (either works if `plugin.json`/csproj agree; nopCommerce looks for a logo file in the plugin folder).

## plugin.json

```json
{
  "Group": "Widgets",
  "FriendlyName": "My widget",
  "SystemName": "Widgets.MyWidget",
  "Version": "1.00",
  "SupportedVersions": [ "4.90" ],
  "Author": "{Company}",
  "DisplayOrder": 1,
  "FileName": "Nop.Plugin.Widgets.MyWidget.dll",
  "Description": "One sentence shown in the plugin list."
}
```

- `SupportedVersions` must contain the major version (`"4.90"`), never a minor (`"4.90.8"`). A plugin can list several only if one build truly runs on all of them.
- `Version` is the plugin's own version. Raising it makes nopCommerce call `UpdateAsync(currentVersion, targetVersion)` and run `MigrationProcessType.Update` migrations on next start.
- Optional: `"LimitedToStores": []`, `"LimitedToCustomerRoles": []`, `"DependsOnSystemNames": []`.

## Plugin class

```csharp
using Nop.Core.Domain.Cms;
using Nop.Services.Cms;
using Nop.Services.Configuration;
using Nop.Services.Localization;
using Nop.Services.Plugins;
using Nop.Web.Framework.Infrastructure;
using Nop.Web.Framework.Mvc.Routing;

namespace Nop.Plugin.Widgets.MyWidget;

public class MyWidgetPlugin : BasePlugin, IWidgetPlugin
{
    protected readonly ILocalizationService _localizationService;
    protected readonly INopUrlHelper _nopUrlHelper;
    protected readonly ISettingService _settingService;
    protected readonly WidgetSettings _widgetSettings;

    public MyWidgetPlugin(ILocalizationService localizationService,
        INopUrlHelper nopUrlHelper,
        ISettingService settingService,
        WidgetSettings widgetSettings)
    {
        _localizationService = localizationService;
        _nopUrlHelper = nopUrlHelper;
        _settingService = settingService;
        _widgetSettings = widgetSettings;
    }

    public override string GetConfigurationPageUrl()
    {
        return _nopUrlHelper.RouteUrl(MyWidgetDefaults.ConfigurationRouteName);
    }

    public Task<IList<string>> GetWidgetZonesAsync()
    {
        return Task.FromResult<IList<string>>(new List<string> { PublicWidgetZones.ProductDetailsTop });
    }

    public Type GetWidgetViewComponent(string widgetZone)
    {
        ArgumentNullException.ThrowIfNull(widgetZone);
        return typeof(Components.MyWidgetViewComponent);
    }

    public override async Task InstallAsync()
    {
        await _settingService.SaveSettingAsync(new MyWidgetSettings { /* defaults */ });

        if (!_widgetSettings.ActiveWidgetSystemNames.Contains(MyWidgetDefaults.SystemName))
        {
            _widgetSettings.ActiveWidgetSystemNames.Add(MyWidgetDefaults.SystemName);
            await _settingService.SaveSettingAsync(_widgetSettings);
        }

        await _localizationService.AddOrUpdateLocaleResourceAsync(new Dictionary<string, string>
        {
            ["Plugins.Widgets.MyWidget.Fields.Message"] = "Message",
            ["Plugins.Widgets.MyWidget.Fields.Message.Hint"] = "Text shown on the product page."
        });

        await base.InstallAsync();
    }

    public override async Task UninstallAsync()
    {
        if (_widgetSettings.ActiveWidgetSystemNames.Contains(MyWidgetDefaults.SystemName))
        {
            _widgetSettings.ActiveWidgetSystemNames.Remove(MyWidgetDefaults.SystemName);
            await _settingService.SaveSettingAsync(_widgetSettings);
        }

        await _settingService.DeleteSettingAsync<MyWidgetSettings>();
        await _localizationService.DeleteLocaleResourcesAsync("Plugins.Widgets.MyWidget");

        await base.UninstallAsync();
    }

    public bool HideInWidgetList => false;
}
```

`INopUrlHelper.RouteUrl(...)` exists only from **4.90**. For 4.70/4.80 either inject `IUrlHelperFactory` + `IActionContextAccessor` (what core did in 4.80) or return `$"{_webHelper.GetStoreLocation()}Admin/MyWidget/Configure"` with `IWebHelper`.

## IPlugin lifecycle (4.90)

`BasePlugin` implements everything virtually; override only what you need:

| Method | Called when |
|---|---|
| `InstallAsync()` | Admin installs the plugin (after the restart). Seed settings, locales, schedule tasks. |
| `InstallSampleDataAsync()` | **New in 4.90.** During store installation with sample data. Default does nothing. |
| `UpdateAsync(string currentVersion, string targetVersion)` | `Version` in plugin.json changed. Prefer `NopMigration` with `MigrationProcessType.Update` for schema/locale changes. |
| `PreparePluginToUninstallAsync()` | When the admin marks the plugin for uninstall. Throw an exception to block it (e.g. other plugins must be removed first). |
| `UninstallAsync()` | Remove everything you added. |
| `GetConfigurationPageUrl()` | Link for the "Configure" button. |

Plugin-type interfaces (signatures unchanged between 4.70 and 4.90): `IWidgetPlugin`, `IPaymentMethod`, `IShippingRateComputationMethod`, `IPickupPointProvider`, `ITaxProvider`, `IDiscountRequirementRule`, `IExternalAuthenticationMethod`, `IMultiFactorAuthenticationMethod`, `IExchangeRateProvider`, `ISearchProvider`, `IMiscPlugin`. Copy their member list from the target version's `src/Libraries/Nop.Services` when implementing one.
