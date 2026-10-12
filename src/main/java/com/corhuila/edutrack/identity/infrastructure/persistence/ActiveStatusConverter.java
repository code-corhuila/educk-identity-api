package com.corhuila.edutrack.identity.infrastructure.persistence;

import jakarta.persistence.AttributeConverter;
import jakarta.persistence.Converter;

/** Maps the existing database status without altering the domain boolean. */
@Converter
public class ActiveStatusConverter implements AttributeConverter<Boolean, String> {
    @Override public String convertToDatabaseColumn(Boolean active) {
        return Boolean.TRUE.equals(active) ? "ACTIVE" : "INACTIVE";
    }
    @Override public Boolean convertToEntityAttribute(String status) {
        return "ACTIVE".equals(status);
    }
}
