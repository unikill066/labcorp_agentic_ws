from pydantic import BaseModel


class Job(BaseModel):
    """
    Represents the data structure of a Venue.
    """

    title: str
    location: str
    category: str
    job_id: str
    url: str
