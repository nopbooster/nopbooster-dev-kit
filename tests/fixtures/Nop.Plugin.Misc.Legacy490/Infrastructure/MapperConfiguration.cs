using AutoMapper;
using Nop.Core.Infrastructure.Mapper;
using Nop.Plugin.Misc.Legacy490.Domain;
using Nop.Plugin.Misc.Legacy490.Models;

namespace Nop.Plugin.Misc.Legacy490.Infrastructure;

public class MapperConfiguration : Profile, IOrderedMapperProfile
{
    public MapperConfiguration()
    {
        CreateMap<LegacyRecord, LegacyRecordModel>()
            .ForMember(model => model.CreatedOn, options => options.Ignore());
    }

    public int Order => 1;
}
