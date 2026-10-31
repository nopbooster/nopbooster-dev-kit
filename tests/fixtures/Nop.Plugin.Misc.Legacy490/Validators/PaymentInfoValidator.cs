using FluentValidation;
using Nop.Plugin.Misc.Legacy490.Models;
using Nop.Web.Framework.Validators;

namespace Nop.Plugin.Misc.Legacy490.Validators;

public class PaymentInfoValidator : BaseNopValidator<PaymentInfoModel>
{
    public PaymentInfoValidator()
    {
        RuleFor(x => x.CardNumber).IsCreditCard().WithMessage("Wrong card number");
    }
}
