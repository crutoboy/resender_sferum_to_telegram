"""
Классы для работы с ответами от API

:copyright: (c) 2024 by l2700l.
:license: MIT, see LICENSE for more details.
:author: l2700l <thetypgame@gmail.com>
"""

from .calls import CallStart, Conversation, PeerCallEnd
from .channels import ChannelHistory
from .messages import Message, MessagesHistory
from .users import UserCredentials, AnonCredentials
from .response import Response
