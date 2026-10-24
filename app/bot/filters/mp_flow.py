from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext


class MpFlowFilter(BaseFilter):
    async def __call__(self, _event: object, state: FSMContext) -> bool:
        data = await state.get_data()
        return bool(data.get("mp_flow"))
