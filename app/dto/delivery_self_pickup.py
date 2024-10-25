import pydantic

from app.dto import common as dto_common


class DeliverySelfPickupTimes(pydantic.BaseModel):
    time_start: dto_common.StrTime
    time_stop: dto_common.StrTime

    def clear(self):
        self.time_start = None
        self.time_stop = None


class DeliverySelfPickupWeekDays(pydantic.BaseModel):
    monday: DeliverySelfPickupTimes | None = None
    tuesday: DeliverySelfPickupTimes | None = None
    wednesday: DeliverySelfPickupTimes | None = None
    thursday: DeliverySelfPickupTimes | None = None
    friday: DeliverySelfPickupTimes | None = None
    saturday: DeliverySelfPickupTimes | None = None
    sunday: DeliverySelfPickupTimes | None = None


class DeliverySelfPickup(dto_common.TGStoreShopEntitiesBaseModel):
    title: str
    description: str | None = None
    contact_phone: str | None = None
    contact_tg_username: str
    schedule: DeliverySelfPickupWeekDays


class DeliverySelfPickupCreateRequest(dto_common.TGStoreBaseRequest):
    title: str
    description: str | None = None
    contact_phone: str | None = None
    contact_tg_username: str | None = None
    schedule: DeliverySelfPickupWeekDays | None = None


class DeliverySelfPickupUpdateRequest(DeliverySelfPickupCreateRequest):
    title: str | None = None

class DeliverySelfPickupUpdate(dto_common.TGStoreEntityBaseUpdateModel, DeliverySelfPickupUpdateRequest):
    pass
