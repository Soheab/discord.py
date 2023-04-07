"""
The MIT License (MIT)

Copyright (c) 2015-present Rapptz

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Any, Literal, Optional, overload, Union, Mapping, Sequence, Dict, List, Tuple, Generator


from . import abc
from .partial_emoji import PartialEmoji, _EmojiTag

from .channel import ForumTag
from .utils import MISSING, _bytes_to_base64_data, time_snowflake, utcnow
from .enums import (
    VerificationLevel, NotificationLevel, ContentFilter, ChannelType, VideoQualityMode,
    ForumLayoutType, ForumOrderType,
)
from .message import EmojiInputType
from .flags import SystemChannelFlags
from .guild import Guild

if TYPE_CHECKING:
    from .abc import Snowflake
    from .role import Role
    from .permissions import PermissionOverwrite, Permissions
    from .colour import Colour
    from .state import ConnectionState


class CreateGuildRole:
    def __init__(
        self,
        name: str,
        *,
        colour: Colour = MISSING,
        hoist: bool = MISSING,
        icon: Optional[bytes] = MISSING,
        unicode_emoji: Optional[PartialEmoji] = MISSING,
        position: int = MISSING,
        permissions: Permissions = MISSING,
        tags: Optional[Sequence[_EmojiTag]] = MISSING,
    ) -> None:
        self.id: int = time_snowflake(utcnow())
        self.name: str = name
        self.colour: Colour = colour
        self.hoist: bool = hoist
        self.icon: Optional[bytes] = icon
        self.unicode_emoji: Optional[PartialEmoji] = unicode_emoji
        self.hoist: bool = hoist
        self.position: int = position
        self.permissions: Permissions = permissions
        self.tags: Optional[Sequence[_EmojiTag]] = tags

    def _to_dict(self) -> Dict[str, Any]:
        base = {
            'id': self.id,
            'name': self.name,
            'hoist': self.hoist,
            'permissions': self.permissions.value,
        }
        if self.colour is not MISSING:
            base['color'] = self.colour.value
        if self.icon is not MISSING:
            base['icon'] = self.icon
        if self.unicode_emoji is not MISSING:
            base['unicode_emoji'] = self.unicode_emoji
        if self.tags:
            base['tags'] = self.tags

        return base
        
class CreateGuildChannel:
    def __init__(
        self,
        channel_type: ChannelType,
        name: str,
        *,
        position: int = MISSING,
        overwrites: Mapping[Union[Snowflake, CreateGuildRole], PermissionOverwrite] = MISSING,
        **options: Any
    ) -> None:
        self.id: int = time_snowflake(utcnow())
        self.type: ChannelType = channel_type
        self.name: str = name
        self.position: int = position
        self.overwrites: Mapping[Union[Snowflake, CreateGuildRole], PermissionOverwrite] = overwrites
        self._options: Dict[str, Any] = options

    def _to_dict(self) -> Dict[str, Any]:
        payload = {
            'id': self.id,
            'type': self.type.value,
            'name': self.name,
            **self._options.copy()
        }
        if self.position is not MISSING:
            payload['position'] = self.position
        if self.overwrites:
            payload['permission_overwrites'] = self.overwrites
        return payload

class CreateGuild:
    def __init__(
        self,
        *,
        name: str,
        icon: bytes = MISSING,
        afk_timeout: Optional[int] = None,
        afk_channel: Optional[CreateGuildChannel] = None,
        system_channel: Optional[CreateGuildChannel] = None,
        system_channel_flags: Optional[SystemChannelFlags] = None,
        verification_level: VerificationLevel = VerificationLevel.none,
        default_message_notifications: NotificationLevel = NotificationLevel.all_messages,
        explicit_content_filter: ContentFilter = ContentFilter.disabled,
    ) -> None:
        self._state: ConnectionState = MISSING

        self._channels: Dict[int, CreateGuildChannel] = {}
        self._roles: Dict[int, CreateGuildRole] = {}

        self.name: str = name
        self.icon: bytes = icon
        self.afk_timeout: Optional[int] = afk_timeout

        self._afk_channel: Optional[CreateGuildChannel] = afk_channel
        self._system_channel: Optional[CreateGuildChannel] = system_channel

        self.system_channel_flags: Optional[SystemChannelFlags] = system_channel_flags
        if system_channel_flags and not isinstance(system_channel_flags, SystemChannelFlags):
            raise TypeError('system_channel_flags must be a SystemChannelFlags')

        self.verification_level: VerificationLevel = verification_level
        if verification_level and not isinstance(verification_level, VerificationLevel):
            raise TypeError('verification_level must be a VerificationLevel')

        self.default_message_notifications: NotificationLevel = default_message_notifications
        if default_message_notifications and not isinstance(default_message_notifications, NotificationLevel):
            raise TypeError('default_message_notifications must be a NotificationLevel')

        self.explicit_content_filter: ContentFilter = explicit_content_filter
        if explicit_content_filter and not isinstance(explicit_content_filter, ContentFilter):
            raise TypeError('explicit_content_filter must be a ContentFilter')

    async def __await__(self) -> Generator[Any, None, Guild]:
        return self.create().__await__()
    
    def _with_state(self, state: ConnectionState) -> CreateGuild:
        self._state = state
        return self

    async def create(self) -> Guild:
        data = await self._state.http.create_guild(**self._to_dict())
        return Guild(data=data, state=self._state)

    @property
    def channels(self) -> List[CreateGuildChannel]:
        return list(self._channels.values())
    
    @property
    def roles(self) -> List[CreateGuildRole]:
        return list(self._roles.values())


    @property
    def system_channel(self) -> Optional[CreateGuildChannel]:
        return self._system_channel

    @system_channel.setter
    def system_channel(self, value: Optional[CreateGuildChannel]) -> None:
        if value and not isinstance(value, CreateGuildChannel):
            raise TypeError('system_channel must be a CreateGuildChannel')
        self._system_channel = value

    @property
    def afk_channel(self) -> Optional[CreateGuildChannel]:
        return self._afk_channel
    
    @afk_channel.setter
    def afk_channel(self, value: Optional[CreateGuildChannel]) -> None:
        if value and not isinstance(value, CreateGuildChannel):
            raise TypeError('afk_channel must be a CreateGuildChannel')
        self._afk_channel = value
    
    
    def get_channel(self, id: int, /) -> Optional[CreateGuildChannel]:
        return self._channels.get(id)
    
    def get_role(self, id: int, /) -> Optional[CreateGuildRole]:
        return self._roles.get(id)

    def _to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            'name': self.name,
            'verification_level': self.verification_level.value,
            'default_message_notifications': self.default_message_notifications.value,
            'explicit_content_filter': self.explicit_content_filter.value,
        }

        if self.icon is not MISSING:
            payload['icon'] = _bytes_to_base64_data(self.icon)

        if self.afk_timeout is not None:
            payload['afk_timeout'] = self.afk_timeout

        if self.system_channel_flags is not None:
            payload['system_channel_flags'] = self.system_channel_flags.value

        if self.afk_channel is not None:
            payload['afk_channel_id'] = self.afk_channel.id
        
        if self.system_channel is not None:
            payload['system_channel_id'] = self.system_channel.id

        if self._channels:
            payload['channels'] = [channel._to_dict() for channel in self._channels.values()]
        if self._roles:
            payload['roles'] = [role._to_dict() for role in self._roles.values()]

        return payload

    @overload
    async def add_channel(
        self,
        channel_type: Literal[ChannelType.text],
        /,
        name: str,
        *,
        position: int = MISSING,
        overwrites: Mapping[Union[Snowflake, CreateGuildRole], PermissionOverwrite] = MISSING,
        category: Optional[CreateGuildChannel] = None,
        news: bool = False,
        topic: str = MISSING,
        slowmode_delay: int = MISSING,
        nsfw: bool = MISSING,
        default_auto_archive_duration: int = MISSING,
        default_thread_slowmode_delay: int = MISSING,
        system_channel: bool = False,
    ):
        ...
    
    @overload
    async def add_channel(
        self,
        channel_type: Literal[ChannelType.voice],
        /,
        name: str,
        *,
        position: int = MISSING,
        overwrites: Mapping[Union[Snowflake, CreateGuildRole], PermissionOverwrite] = MISSING,
        category: Optional[CreateGuildChannel] = None,
        bitrate: int = MISSING,
        user_limit: int = MISSING,
        rtc_region: Optional[str] = MISSING,
        video_quality_mode: VideoQualityMode = MISSING,
        afk_channel: bool = False,
    ):
        ...

    @overload
    async def add_channel(
        self,
        channel_type: Literal[ChannelType.stage_voice],
        /,
        name: str,
        *,
        position: int = MISSING,
        overwrites: Mapping[Union[Snowflake, CreateGuildRole], PermissionOverwrite] = MISSING,
        category: Optional[CreateGuildChannel] = None,
        bitrate: int = MISSING,
        user_limit: int = MISSING,
        rtc_region: Optional[str] = MISSING,
        video_quality_mode: VideoQualityMode = MISSING,
    ):
        ...

    @overload
    async def add_channel(
        self,
        channel_type: Literal[ChannelType.category],
        /,
        name: str,
        *,
        position: int = MISSING,
        overwrites: Mapping[Union[Snowflake, CreateGuildRole], PermissionOverwrite] = MISSING,
    ):
        ...

    @overload
    async def add_channel(
        self,
        channel_type: Literal[ChannelType.forum],
        /,
        name: str,
        *,
        position: int = MISSING,
        overwrites: Mapping[Union[Snowflake, CreateGuildRole], PermissionOverwrite] = MISSING,
        topic: str = MISSING,
        category: Optional[CreateGuildChannel] = None,
        slowmode_delay: int = MISSING,
        nsfw: bool = MISSING,
        default_auto_archive_duration: int = MISSING,
        default_thread_slowmode_delay: int = MISSING,
        default_sort_order: ForumOrderType = MISSING,
        default_reaction_emoji: EmojiInputType = MISSING,
        default_layout: ForumLayoutType = MISSING,
        available_tags: Sequence[ForumTag] = MISSING,
    ):
        ...

    async def add_channel(
        self,
        channel_type: ChannelType,
        /
        name: str,
        *,
        position: int = MISSING,
        overwrites: Mapping[Union[Snowflake, CreateGuildRole], PermissionOverwrite] = MISSING,
        **kwargs: Any,
    ):
        kwargs_per_type: Dict[ChannelType, Tuple[str, ...]]= {
            ChannelType.text: ('category', 'news', 'topic', 'slowmode_delay', 'nsfw', 'overwrites', 'default_auto_archive_duration', 'default_thread_slowmode_delay'),
            ChannelType.voice: ('category', 'bitrate', 'user_limit', 'rtc_region', 'video_quality_mode', 'overwrites'),
            ChannelType.stage_voice: ('category', 'bitrate', 'user_limit', 'rtc_region', 'video_quality_mode', 'overwrites'),
            ChannelType.category: ('overwrites',),
            ChannelType.forum: (
                'topic', 'category', 'slowmode_delay', 'nsfw', 'overwrites', 'default_auto_archive_duration', 'default_thread_slowmode_delay',
                'default_sort_order', 'default_reaction_emoji', 'default_layout', 'available_tags'
            ),
        }

        if channel_type not in kwargs_per_type:
            raise TypeError(f'Invalid channel type {type!r}. Expected one of {tuple(kwargs_per_type.keys())!r}')
        

        if overwrites is MISSING:
            overwrites = {}
        elif not isinstance(overwrites, Mapping):
            raise TypeError('overwrites parameter expects a dict.')
        
        perms = []
        for target, perm in overwrites.items():
            if not isinstance(perm, PermissionOverwrite):
                raise TypeError(f'Expected PermissionOverwrite received {perm.__class__.__name__}')

            allow, deny = perm.pair()
            payload = {'allow': allow.value, 'deny': deny.value, 'id': target.id}

            if isinstance(target, Role):
                payload['type'] = abc._Overwrites.ROLE
            else:
                payload['type'] = abc._Overwrites.MEMBER

            perms.append(payload)

        
        options = {}

        if channel_type is not ChannelType.category:
            category = kwargs.pop('category', MISSING)
            parent_id = category.id if category else None
            if parent_id:
                if parent_id not in self._channels:
                    raise ValueError(f"No such category with ID {parent_id}")

                options["parent_id"] = parent_id

        elif channel_type is ChannelType.forum:
            default_auto_archive_duration = kwargs.pop('default_auto_archive_duration', MISSING)
            if default_auto_archive_duration is not MISSING:
                options['default_auto_archive_duration'] = default_auto_archive_duration

            default_thread_slowmode_delay = kwargs.pop('default_thread_slowmode_delay', MISSING)
            if default_thread_slowmode_delay is not MISSING:
                options['default_thread_rate_limit_per_user'] = default_thread_slowmode_delay


            default_sort_order = kwargs.pop('default_sort_order', MISSING)
            if default_sort_order is not MISSING:
                if not isinstance(default_sort_order, ForumOrderType):
                    raise TypeError(
                        f'default_sort_order parameter must be a ForumOrderType not {default_sort_order.__class__.__name__}'
                    )

                options['default_sort_order'] = default_sort_order.value

            default_reaction_emoji = kwargs.pop('default_reaction_emoji', MISSING)
            if default_reaction_emoji is not MISSING:
                if isinstance(default_reaction_emoji, _EmojiTag):
                    options['default_reaction_emoji'] = default_reaction_emoji._to_partial()._to_forum_tag_payload()
                elif isinstance(default_reaction_emoji, str):
                    options['default_reaction_emoji'] = PartialEmoji.from_str(default_reaction_emoji)._to_forum_tag_payload()
                else:
                    raise ValueError(f'default_reaction_emoji parameter must be either Emoji, PartialEmoji, or str')

            default_layout = kwargs.pop('default_layout', MISSING)
            if default_layout is not MISSING:
                if not isinstance(default_layout, ForumLayoutType):
                    raise TypeError(
                        f'default_layout parameter must be a ForumLayoutType not {default_layout.__class__.__name__}'
                    )

                options['default_forum_layout'] = default_layout.value

            available_tags = kwargs.pop('available_tags', MISSING)
            if available_tags is not MISSING:
                options['available_tags'] = [t.to_dict() for t in available_tags]


        elif channel_type in (ChannelType.stage_voice, ChannelType.voice):
            rtc_region = kwargs.pop('rtc_region', MISSING)
            if rtc_region is not MISSING:
                options['rtc_region'] = None if rtc_region is None else rtc_region

            video_quality_mode = kwargs.pop('video_quality_mode', MISSING)
            if video_quality_mode is not MISSING:
                if not isinstance(video_quality_mode, VideoQualityMode):
                    raise TypeError('video_quality_mode must be of type VideoQualityMode')
                options['video_quality_mode'] = video_quality_mode.value


        for arg in kwargs_per_type[channel_type]:
            value = kwargs.get(arg, MISSING)
            if value is not MISSING:
                options[arg] = value

        channel = CreateGuildChannel(channel_type, name, overwrites=overwrites, position=position, **options)
        if channel_type is ChannelType.text:
            if kwargs.get('system_channel', False):
                self.system_channel = channel
        elif channel_type is ChannelType.voice:
            if kwargs.get('afk_channel', False):
                self.afk_channel = channel

        self._channels[channel.id] = channel
        return channel
            



    @overload
    async def create_role(
        self,
        name: str,
        *,
        permissions: Permissions = ...,
        colour: Union[Colour, int] = ...,
        hoist: bool = ...,
        display_icon: Union[bytes, str] = MISSING,
        mentionable: bool = ...,
    ) -> CreateGuildRole:
        ...

    @overload
    async def create_role(
        self,
        name: str,
        *,
        permissions: Permissions = ...,
        color: Union[Colour, int] = ...,
        hoist: bool = ...,
        display_icon: Union[bytes, str] = MISSING,
        mentionable: bool = ...,
    ) -> CreateGuildRole:
        ...

    async def create_role(
        self,
        name: str,
        *,
        permissions: Permissions = MISSING,
        color: Union[Colour, int] = MISSING,
        colour: Union[Colour, int] = MISSING,
        hoist: bool = MISSING,
        display_icon: Union[bytes, str] = MISSING,
        mentionable: bool = MISSING,
    ) -> CreateGuildRole:

        options: Dict[str, Any] = {}
        if permissions is not MISSING:
            options['permissions'] = str(permissions.value)
        else:
            options['permissions'] = '0'

        actual_colour = colour or color or Colour.default()
        if isinstance(actual_colour, int):
            options['color'] = actual_colour
        else:
            options['color'] = actual_colour.value

        if hoist is not MISSING:
            options['hoist'] = hoist

        if display_icon is not MISSING:
            if isinstance(display_icon, bytes):
                options['icon'] = _bytes_to_base64_data(display_icon)
            else:
                options['unicode_emoji'] = display_icon

        if mentionable is not MISSING:
            options['mentionable'] = mentionable

        role = CreateGuildRole(name, **options)
        self._roles[role.id] = role
        return role