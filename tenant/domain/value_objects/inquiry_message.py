from dataclasses import dataclass
from ..exceptions import EmptyInquiryMessageException


@dataclass(frozen=True)
class InquiryMessage:
    content: str
    MAX_LENGTH: int = 2000
    MIN_LENGTH: int = 3

    def __post_init__(self):
        if not isinstance(self.content, str):
            raise EmptyInquiryMessageException("Inquiry message must be text.")

        stripped = self.content.strip()
        if len(stripped) < self.MIN_LENGTH:
            raise EmptyInquiryMessageException(
                f"Inquiry message must be at least {self.MIN_LENGTH} characters long."
            )

        if len(stripped) > self.MAX_LENGTH:
            raise EmptyInquiryMessageException(
                f"Inquiry message cannot exceed {self.MAX_LENGTH} characters."
            )

        object.__setattr__(self, "content", stripped)

    def __str__(self) -> str:
        return self.content
